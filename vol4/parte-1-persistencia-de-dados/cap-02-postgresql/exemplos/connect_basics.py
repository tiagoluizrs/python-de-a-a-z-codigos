"""Conectar, consultar, tipos ricos, erros."""
import datetime as dt
import decimal
import uuid

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from pgenv import DSN

print("psycopg", psycopg.__version__, "| libpq", psycopg.pq.version(), "| implementação:", psycopg.pq.__impl__)

with psycopg.connect(DSN, row_factory=dict_row) as conn:       # sai do bloco: COMMIT (ou ROLLBACK) e FECHA a conexão
    print(conn.execute("SELECT version() AS v").fetchone()["v"][:40], "...")
    conn.execute("DROP TABLE IF EXISTS demo")
    conn.execute("""CREATE TABLE demo (
        id uuid PRIMARY KEY, name text NOT NULL, price numeric(10, 2), created timestamptz DEFAULT now(),
        tags text[], meta jsonb)""")

    row = conn.execute(
        "INSERT INTO demo (id, name, price, tags, meta) VALUES (%s, %s, %s, %s, %s) RETURNING *",
        (uuid.uuid4(), "caneta", decimal.Decimal("9.90"), ["a", "b"], Jsonb({"cor": "azul", "dims": [1, 2]})),
    ).fetchone()
    conn.commit()                                             # sem commit, o rollback de um erro abaixo desfaria TUDO, até o CREATE
    print("tipos que VOLTAM como Python:")
    for key, value in row.items():
        print(f"  {key:<8} {type(value).__name__:<10} {value!r}")

    # numeric volta como Decimal (nunca float!), timestamptz volta com fuso
    assert isinstance(row["price"], decimal.Decimal) and row["created"].tzinfo is not None

    # consultas em jsonb e arrays
    print("jsonb ->>:", conn.execute("SELECT meta ->> 'cor' AS cor FROM demo").fetchone()["cor"],
          "| array ANY:", conn.execute("SELECT count(*) AS n FROM demo WHERE %s = ANY(tags)", ("a",)).fetchone()["n"])

    # parâmetros: %s (não ? como no SQLite), SEMPRE, nunca f-string
    evil = "x'; DROP TABLE demo; --"
    print("injeção como VALOR é inofensiva:", conn.execute("SELECT count(*) AS n FROM demo WHERE name = %s", (evil,)).fetchone())

    # erros têm classes por SQLSTATE
    try:
        conn.execute("INSERT INTO demo (id, name) VALUES (%s, NULL)", (uuid.uuid4(),))
    except psycopg.errors.NotNullViolation as error:
        print("NotNullViolation: sqlstate", error.sqlstate, "| coluna:", error.diag.column_name)
        conn.rollback()                                       # depois de um erro a transação fica ABORTADA até o rollback
    try:
        conn.execute("SELECT 1/0")
    except psycopg.errors.DivisionByZero as error:
        print("DivisionByZero: sqlstate", error.sqlstate)
        conn.rollback()
    conn.execute("DROP TABLE demo")
