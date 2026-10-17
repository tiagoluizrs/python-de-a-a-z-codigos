"""SQLAlchemy Core: engine, text(), tabelas, select/insert/update/delete."""
import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, Integer, MetaData, Numeric, String, Table, func, select

print("SQLAlchemy", sa.__version__)
engine = sa.create_engine("sqlite://", echo=False)             # echo=True imprime todo o SQL

# 1. SQL puro com parâmetros nomeados: text()
with engine.begin() as conn:                                  # begin(): commit ao sair, rollback se houver exceção
    conn.execute(sa.text("CREATE TABLE raw (id INTEGER PRIMARY KEY, name TEXT)"))
    conn.execute(sa.text("INSERT INTO raw (name) VALUES (:name)"), [{"name": "a"}, {"name": "b"}])
    print("text():", conn.execute(sa.text("SELECT * FROM raw WHERE name = :n"), {"n": "b"}).all())

# 2. a linguagem de expressões: o MESMO código gera SQL para QUALQUER banco
metadata = MetaData()
author = Table("author", metadata, Column("id", Integer, primary_key=True), Column("name", String(50), nullable=False, unique=True))
book = Table("book", metadata, Column("id", Integer, primary_key=True), Column("title", String(80), nullable=False),
             Column("price", Numeric(10, 2), nullable=False), Column("author_id", ForeignKey("author.id"), nullable=False))
metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(author.insert(), [{"name": "Machado"}, {"name": "Clarice"}])
    ids = {row.name: row.id for row in conn.execute(select(author))}
    conn.execute(book.insert(), [
        {"title": "Dom Casmurro", "price": "39.90", "author_id": ids["Machado"]},
        {"title": "Memórias Póstumas", "price": "42.50", "author_id": ids["Machado"]},
        {"title": "A Hora da Estrela", "price": "35.00", "author_id": ids["Clarice"]}])

    query = (select(author.c.name, func.count(book.c.id).label("books"), func.sum(book.c.price).label("total"))
             .join(book, book.c.author_id == author.c.id).group_by(author.c.name).having(func.count(book.c.id) >= 1)
             .order_by(func.sum(book.c.price).desc()))
    print("SQL gerado:", " ".join(str(query).split()))
    for row in conn.execute(query):
        print("  Row por atributo:", row.name, row.books, row.total)
    print("  .mappings():", conn.execute(select(author.c.name).limit(1)).mappings().first())
    conn.execute(book.update().where(book.c.title.like("Dom%")).values(price=book.c.price * 2))
    conn.execute(book.delete().where(book.c.price > 80))
    print("depois de update/delete:", conn.execute(select(func.count()).select_from(book)).scalar_one(), "livros")

# 3. WITH RECURSIVE e janelas no mesmo estilo
cte = select(func.row_number().over(order_by=book.c.price.desc()).label("rank"), book.c.title, book.c.price).cte("ranked")
with engine.connect() as conn:
    print("janela:", [tuple(r) for r in conn.execute(select(cte).where(cte.c.rank <= 2))])
