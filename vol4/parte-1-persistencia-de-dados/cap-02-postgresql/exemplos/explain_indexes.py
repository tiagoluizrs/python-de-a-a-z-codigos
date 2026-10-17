"""Índices no PostgreSQL: EXPLAIN ANALYZE, B-tree, GIN em jsonb, paginação."""
import json
import time

import psycopg
from psycopg.rows import dict_row

from pgenv import DSN


def plan(conn, sql, params=()):
    node = conn.execute("EXPLAIN (ANALYZE, FORMAT JSON) " + sql, params).fetchone()["QUERY PLAN"][0]
    top = node["Plan"]
    while "Plans" in top and top["Node Type"] in ("Gather", "Limit", "Aggregate", "Finalize Aggregate"):
        top = top["Plans"][0]
    return top["Node Type"], node["Execution Time"]


with psycopg.connect(DSN, row_factory=dict_row, autocommit=True) as conn:
    conn.execute("DROP TABLE IF EXISTS ev")
    conn.execute("CREATE TABLE ev (id bigserial PRIMARY KEY, email text, kind int, payload jsonb)")
    conn.execute("""INSERT INTO ev (email, kind, payload)
        SELECT 'user' || g || '@x.com', g % 50, jsonb_build_object('tag', 'tag' || (g % 1000), 'n', g)
        FROM generate_series(1, 500000) g""")
    conn.execute("ANALYZE ev")

    query = "SELECT * FROM ev WHERE email = %s"
    node, ms = plan(conn, query, ("user250000@x.com",))
    print(f"sem índice : {node:<24} {ms:8.2f} ms")
    conn.execute("CREATE INDEX ev_email ON ev (email)")
    node, ms = plan(conn, query, ("user250000@x.com",))
    print(f"B-tree     : {node:<24} {ms:8.3f} ms")

    jq = "SELECT count(*) FROM ev WHERE payload @> %s::jsonb"
    node, ms = plan(conn, jq, (json.dumps({"tag": "tag7"}),))
    print(f"jsonb sem índice: {node:<20} {ms:8.2f} ms")
    conn.execute("CREATE INDEX ev_payload ON ev USING gin (payload)")
    node, ms = plan(conn, jq, (json.dumps({"tag": "tag7"}),))
    print(f"jsonb com GIN   : {node:<20} {ms:8.3f} ms")

    # paginação: OFFSET relê e descarta; keyset (id > último) vai direto
    start = time.perf_counter()
    for _ in range(20):
        conn.execute("SELECT id FROM ev ORDER BY id LIMIT 50 OFFSET 400000").fetchall()
    offset_time = (time.perf_counter() - start) / 20
    start = time.perf_counter()
    for _ in range(20):
        conn.execute("SELECT id FROM ev WHERE id > 400000 ORDER BY id LIMIT 50").fetchall()
    keyset_time = (time.perf_counter() - start) / 20
    print(f"página 8.000 (50 linhas): OFFSET {offset_time * 1e3:.2f} ms | keyset {keyset_time * 1e3:.2f} ms ({offset_time / keyset_time:.0f}x)")

    conn.execute("DROP TABLE ev")
