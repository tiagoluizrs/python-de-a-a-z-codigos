"""Carga em massa: laço, executemany, pipeline e COPY."""
import decimal
import time

import psycopg

from pgenv import DSN

ROWS = [(f"item-{i}", decimal.Decimal("1.50")) for i in range(5_000)]


def timed(label, func, conn):
    conn.execute("TRUNCATE bulk")
    start = time.perf_counter()
    func(conn)
    elapsed = time.perf_counter() - start
    count = conn.execute("SELECT count(*) FROM bulk").fetchone()[0]
    print(f"  {label:<34} {elapsed * 1e3:8.1f} ms  ({count:,} linhas)")
    return elapsed


def loop(conn):
    with conn.transaction():
        for row in ROWS:
            conn.execute("INSERT INTO bulk (name, price) VALUES (%s, %s)", row)


def executemany(conn):
    with conn.transaction():
        conn.cursor().executemany("INSERT INTO bulk (name, price) VALUES (%s, %s)", ROWS)


def pipelined_loop(conn):
    with conn.pipeline(), conn.transaction():
        for row in ROWS:
            conn.execute("INSERT INTO bulk (name, price) VALUES (%s, %s)", row)


def copy(conn):
    with conn.transaction(), conn.cursor() as cur, cur.copy("COPY bulk (name, price) FROM STDIN") as writer:
        for row in ROWS:
            writer.write_row(row)


with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("DROP TABLE IF EXISTS bulk")
    conn.execute("CREATE TABLE bulk (id serial PRIMARY KEY, name text, price numeric(10, 2))")
    print(f"inserir {len(ROWS):,} linhas, uma transação, servidor local em contêiner:")
    base = timed("laço de execute() (1 ida e volta/linha)", loop, conn)
    timed("executemany()", executemany, conn)
    timed("laço dentro de um pipeline", pipelined_loop, conn)
    fast = timed("COPY ... FROM STDIN", copy, conn)
    print(f"  COPY foi {base / fast:,.0f}x mais rápido que o laço")

    # COPY também sai: exportar sem carregar tudo na memória
    chunks = 0
    with conn.cursor() as cur, cur.copy("COPY (SELECT name, price FROM bulk LIMIT 3) TO STDOUT") as reader:
        for data in reader:
            chunks += 1
            print("  COPY TO:", bytes(data).decode().strip())
    conn.execute("DROP TABLE bulk")
