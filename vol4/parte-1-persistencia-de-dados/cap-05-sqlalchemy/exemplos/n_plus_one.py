"""O problema N+1 e as soluções: selectinload, joinedload, raiseload."""
import time

import sqlalchemy as sa
from sqlalchemy import ForeignKey, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, joinedload, mapped_column, relationship, selectinload
from sqlalchemy.exc import InvalidRequestError


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
    author: Mapped[Author] = relationship(back_populates="books")


engine = sa.create_engine("sqlite://")
Base.metadata.create_all(engine)
counter = {"n": 0}
event.listen(engine, "before_cursor_execute", lambda *a: counter.__setitem__("n", counter["n"] + 1))

with Session(engine) as session:
    session.add_all([Author(name=f"a{i}", books=[Book(title=f"b{i}-{j}") for j in range(5)]) for i in range(200)])
    session.commit()

print("200 autores x 5 livros; somar os livros de cada autor:")
for label, option in (("lazy (padrão): N+1", None), ("selectinload", selectinload(Author.books)), ("joinedload", joinedload(Author.books))):
    counter["n"] = 0
    with Session(engine) as session:
        query = select(Author)
        if option is not None:
            query = query.options(option)
        start = time.perf_counter()
        total = sum(len(author.books) for author in session.scalars(query).unique())
        elapsed = time.perf_counter() - start
    print(f"  {label:<22} {counter['n']:>4} consultas | {elapsed * 1e3:6.1f} ms | {total} livros")

# raiseload: transforma o N+1 acidental em ERRO imediato (ótimo em testes)
from sqlalchemy.orm import raiseload

with Session(engine) as session:
    author = session.scalars(select(Author).options(raiseload(Author.books))).first()
    try:
        author.books
    except InvalidRequestError as error:
        print("raiseload:", str(error)[:70], "...")
print("regra: selectinload para coleções (1 -> N), joinedload para muitos-para-um; meça com a contagem de consultas")
