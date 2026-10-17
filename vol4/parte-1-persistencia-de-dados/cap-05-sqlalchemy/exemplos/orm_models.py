"""ORM 2.0: modelos tipados, sessão, unidade de trabalho, identidade, estados."""
import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy.orm.exc import DetachedInstanceError


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    born: Mapped[dt.date | None]                                        # `X | None` = coluna NULL-ável (o tipo vem da anotação)
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(80))
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2))
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
    author: Mapped[Author] = relationship(back_populates="books")

    def __repr__(self):
        return f"Book({self.title!r})"


engine = sa.create_engine("sqlite://")
Base.metadata.create_all(engine)
queries = []
event.listen(engine, "before_cursor_execute", lambda conn, cur, stmt, params, ctx, many: queries.append(stmt.split()[0]))

with Session(engine) as session:
    machado = Author(name="Machado", born=dt.date(1839, 6, 21), books=[Book(title="Dom Casmurro", price=Decimal("39.90"))])
    session.add(machado)
    print("depois do add: pendente em session.new?", machado in session.new, "| id ainda", machado.id, "| consultas até aqui:", len(queries))
    session.flush()                                                     # envia o SQL, mas NÃO confirma
    print("depois do flush: id =", machado.id, "| livro.author_id =", machado.books[0].author_id)
    session.commit()

    # mapa de identidade: a mesma linha é SEMPRE o mesmo objeto, dentro da sessão
    same = session.get(Author, machado.id)
    print("identidade:", same is machado, "| session.get usou o mapa (sem consulta nova)")

    # rastreamento de mudanças: a unidade de trabalho só escreve o que mudou
    machado.name = "Machado de Assis"
    print("sujo?", machado in session.dirty, "| ", end="")
    queries.clear()
    session.commit()
    print("commit emitiu:", queries)

    # relacionamentos e consultas modernas (select(), não session.query())
    machado.books.append(Book(title="Memórias Póstumas", price=Decimal("42.50")))
    session.commit()
    expensive = session.scalars(select(Book).where(Book.price > 40).order_by(Book.price)).all()
    print("consulta:", expensive, "| autor do livro:", expensive[0].author.name)

    # expire_on_commit: depois do commit os atributos são recarregados no próximo acesso
    session.commit()
    queries.clear()
    _ = machado.name
    print("acesso após commit emitiu uma consulta de recarga:", queries)

    # rollback desfaz o que ainda não foi confirmado
    session.add(Author(name="Descartado"))
    session.flush()
    session.rollback()
    print("depois do rollback:", session.scalars(select(Author.name)).all())

# fora da sessão, o objeto fica "desligado" (detached)
try:
    machado.books
except DetachedInstanceError as error:
    print("fora da sessão:", type(error).__name__, "- carregar relações exige uma sessão aberta")
