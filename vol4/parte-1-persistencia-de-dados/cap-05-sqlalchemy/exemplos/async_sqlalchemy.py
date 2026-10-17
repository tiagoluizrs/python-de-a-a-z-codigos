"""SQLAlchemy assíncrono: AsyncEngine, AsyncSession e a regra do carregamento explícito."""
import asyncio
import sys
import time
import warnings

import sqlalchemy as sa
from sqlalchemy import ForeignKey, select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

from dburls import URLS


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "aauthor"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "abook"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("aauthor.id"))
    author: Mapped[Author] = relationship(back_populates="books")


async def main():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)              # DDL síncrono dentro do contexto assíncrono
    Session = async_sessionmaker(engine, expire_on_commit=False)   # expire_on_commit=False: objetos usáveis depois do commit

    async with Session() as session:
        session.add(Author(name="Machado", books=[Book(title="Dom Casmurro"), Book(title="Quincas Borba")]))
        await session.commit()

    async with Session() as session:
        author = (await session.scalars(select(Author))).one()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)    # a corrotina interna é descartada: ruído do erro
                author.books                                       # carregamento preguiçoso = E/S escondida: proibido no async
        except (MissingGreenlet, sa.exc.StatementError) as error:
            print("lazy load no async:", type(getattr(error, "orig", error)).__name__, "- carregue de forma EXPLÍCITA")
        author = (await session.scalars(select(Author).options(selectinload(Author.books)))).one()
        print("com selectinload:", [b.title for b in author.books])

    # uma sessão por tarefa: AsyncSession NÃO é segura entre tarefas simultâneas
    async def work(i):
        async with Session() as s:
            return (await s.scalar(select(sa.func.count()).select_from(Book))) + i

    print("gather com uma sessão por tarefa:", await asyncio.gather(*(work(i) for i in range(3))))
    await engine.dispose()

    # o mesmo com o PostgreSQL (psycopg assíncrono)
    try:
        pg = create_async_engine(URLS["postgresql"], pool_size=5)
        async with pg.connect() as conn:
            start = time.perf_counter()
            await asyncio.gather(*(asyncio.create_task(_sleep(pg)) for _ in range(5)))
            print(f"PostgreSQL assíncrono: 5 consultas de 0,1 s em paralelo: {time.perf_counter() - start:.2f} s")
        await pg.dispose()
    except Exception as error:
        print("(PostgreSQL indisponível:", type(error).__name__, ")")


async def _sleep(engine):
    async with engine.connect() as conn:
        await conn.execute(sa.text("SELECT pg_sleep(0.1)"))


if sys.platform == "win32":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)    # psycopg assíncrono no Windows (Capítulo 2)
else:
    asyncio.run(main())
