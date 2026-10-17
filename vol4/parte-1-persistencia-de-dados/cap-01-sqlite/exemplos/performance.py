"""O que realmente importa para o desempenho: transações, índices e PRAGMAs."""
import os
import sqlite3
import tempfile
import time

folder = tempfile.mkdtemp()
ROWS = 300

print(f"1) {ROWS} inserções em um ARQUIVO (cada commit força o disco):")
for journal, synchronous in (("DELETE", "FULL"), ("WAL", "FULL"), ("WAL", "NORMAL")):
    path = os.path.join(folder, f"{journal}_{synchronous}.db")
    conn = sqlite3.connect(path, autocommit=True)
    conn.execute(f"PRAGMA journal_mode = {journal}")
    conn.execute(f"PRAGMA synchronous = {synchronous}")
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    start = time.perf_counter()
    for i in range(ROWS):
        conn.execute("INSERT INTO t (v) VALUES (?)", (str(i),))    # um commit por linha
    per_row = time.perf_counter() - start
    conn.execute("DELETE FROM t")
    start = time.perf_counter()
    conn.execute("BEGIN")
    conn.executemany("INSERT INTO t (v) VALUES (?)", [(str(i),) for i in range(ROWS)])
    conn.execute("COMMIT")
    batch = time.perf_counter() - start
    print(f"   journal={journal:<6} synchronous={synchronous:<6} commit por linha: {per_row:6.2f} s | uma transação: {batch * 1e3:6.1f} ms | {per_row / batch:7,.0f}x")
    conn.close()

print("2) Índice: busca por e-mail em 200.000 linhas")
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE u (id INTEGER PRIMARY KEY, email TEXT, age INTEGER)")
conn.executemany("INSERT INTO u (email, age) VALUES (?, ?)", ((f"user{i}@x.com", i % 90) for i in range(200_000)))
conn.commit()
query = "SELECT * FROM u WHERE email = ?"
print("   plano sem índice:", conn.execute("EXPLAIN QUERY PLAN " + query, ("a",)).fetchall()[0][-1])
start = time.perf_counter()
for _ in range(20):
    conn.execute(query, ("user150000@x.com",)).fetchall()
without = (time.perf_counter() - start) / 20
start = time.perf_counter()
conn.execute("CREATE INDEX ix_u_email ON u (email)")
build = time.perf_counter() - start
print("   plano com índice :", conn.execute("EXPLAIN QUERY PLAN " + query, ("a",)).fetchall()[0][-1])
start = time.perf_counter()
for _ in range(2000):
    conn.execute(query, ("user150000@x.com",)).fetchall()
with_index = (time.perf_counter() - start) / 2000
print(f"   sem índice: {without * 1e3:.2f} ms | com índice: {with_index * 1e6:.1f} us | {without / with_index:,.0f}x mais rápido (criar o índice levou {build * 1e3:.0f} ms)")

print("3) O preço do índice: inserir 50.000 linhas")
for indexed in (False, True):
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE u (id INTEGER PRIMARY KEY, email TEXT, age INTEGER)")
    if indexed:
        c.execute("CREATE INDEX ix ON u (email)")
        c.execute("CREATE INDEX ix2 ON u (age)")
    start = time.perf_counter()
    c.executemany("INSERT INTO u (email, age) VALUES (?, ?)", ((f"user{i}@x.com", i % 90) for i in range(50_000)))
    print(f"   {'com 2 índices' if indexed else 'sem índices  '}: {(time.perf_counter() - start) * 1e3:6.1f} ms")
