"""Ajuda dos exemplos de PostgreSQL: um schema descartável."""
import contextlib
import os
import sys
import time

import psycopg

DSN = os.environ.get("PG_DSN", "postgresql://postgres:postgres@localhost:55432/postgres")


@contextlib.contextmanager
def lab(name="lab60"):
    try:
        conn = psycopg.connect(DSN, autocommit=True, connect_timeout=3)
    except psycopg.OperationalError as error:
        sys.exit(f"PostgreSQL indisponível em {DSN}: {error}\nSuba o contêiner do Capítulo 2 (docker compose up -d).")
    conn.execute(f"DROP SCHEMA IF EXISTS {name} CASCADE")
    conn.execute(f"CREATE SCHEMA {name}")
    conn.execute(f"SET search_path = {name}")
    try:
        yield conn
    finally:
        conn.execute(f"DROP SCHEMA {name} CASCADE")
        conn.close()


def timed(conn, sql, params=None):
    start = time.perf_counter()
    conn.execute(sql, params)
    return time.perf_counter() - start


def plan(conn, sql, params=None):
    """(tipo do nó principal, tempo de execução em ms) de um EXPLAIN ANALYZE."""
    result = conn.execute("EXPLAIN (ANALYZE, FORMAT JSON) " + sql, params).fetchone()[0][0]
    node = result["Plan"]
    while "Plans" in node and node["Node Type"] in ("Gather", "Limit", "Aggregate", "Finalize Aggregate", "Sort"):
        node = node["Plans"][0]
    return node["Node Type"], result["Execution Time"]
