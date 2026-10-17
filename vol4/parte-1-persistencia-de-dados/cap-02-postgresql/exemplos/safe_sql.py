"""Montar SQL com identificadores dinâmicos de forma segura (promessa do Capítulo 8 do Volume 3)."""
import psycopg
from psycopg import sql

from pgenv import DSN

ALLOWED_SORT = {"name", "price"}

with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("DROP TABLE IF EXISTS produto")
    conn.execute('CREATE TABLE produto (name text, price numeric, "ORDER" int)')
    conn.execute("INSERT INTO produto VALUES ('a', 3, 1), ('b', 1, 2)")

    # valores -> %s; NOMES -> sql.Identifier (cita e escapa); trechos fixos -> sql.SQL
    query = sql.SQL("SELECT {cols} FROM {table} ORDER BY {order} {direction}").format(
        cols=sql.SQL(", ").join(map(sql.Identifier, ("name", "ORDER"))),
        table=sql.Identifier("produto"),
        order=sql.Identifier("price"),
        direction=sql.SQL("DESC"),
    )
    print("SQL gerado :", query.as_string(conn))
    print("resultado  :", conn.execute(query).fetchall())

    # Identifier recusa a injeção por construção: o nome vira UM identificador citado
    hostile = 'price"; DROP TABLE produto; --'
    print("hostil     :", sql.SQL("SELECT {c} FROM produto").format(c=sql.Identifier(hostile)).as_string(conn))
    try:
        conn.execute(sql.SQL("SELECT {c} FROM produto").format(c=sql.Identifier(hostile)))
    except psycopg.errors.UndefinedColumn:
        print("             -> UndefinedColumn: tratado como nome de coluna, nunca como SQL; a tabela está intacta:",
              conn.execute("SELECT count(*) FROM produto").fetchone()[0], "linhas")

    # f-string NÃO é aceita onde psycopg espera LiteralString (verificadores de tipo acusam):
    # conn.execute(f"SELECT * FROM produto WHERE name = '{hostile}'")   # <- NÃO FAÇA

    def search(sort_by):
        if sort_by not in ALLOWED_SORT:                      # lista de permissão E Identifier: duas camadas
            raise ValueError(f"ordenação inválida: {sort_by!r}")
        return conn.execute(sql.SQL("SELECT name FROM produto ORDER BY {c}").format(c=sql.Identifier(sort_by))).fetchall()

    print("ordenar por price:", search("price"))
    conn.execute("DROP TABLE produto")
