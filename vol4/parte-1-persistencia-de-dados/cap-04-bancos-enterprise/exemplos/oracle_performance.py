"""Oracle: arraysize/prefetch, executemany, batcherrors e pool."""
import time

import oracledb

from envs import ORACLE

conn = oracledb.connect(**ORACLE)
cursor = conn.cursor()
try:
    cursor.execute("DROP TABLE big PURGE")
except oracledb.DatabaseError:
    pass
cursor.execute("CREATE TABLE big (id NUMBER, v VARCHAR2(30))")

rows = [(i, f"valor {i}") for i in range(20_000)]
start = time.perf_counter()
for row in rows[:500]:
    cursor.execute("INSERT INTO big VALUES (:1, :2)", row)
conn.commit()
loop = (time.perf_counter() - start) * 40
cursor.execute("TRUNCATE TABLE big")
start = time.perf_counter()
cursor.executemany("INSERT INTO big VALUES (:1, :2)", rows)
conn.commit()
many = time.perf_counter() - start
print(f"inserir 20.000 linhas: laço (estimado) {loop:5.1f} s | executemany {many * 1e3:6.1f} ms | {loop / many:,.0f}x")

# arraysize: quantas linhas por ida e volta ao servidor
cursor.execute("TRUNCATE TABLE big")
cursor.executemany("INSERT INTO big VALUES (:1, :2)", [(i, f"valor {i}") for i in range(50_000)])
conn.commit()
print("ler 50.000 linhas (arraysize = prefetchrows):")
for size in (1, 100, 1_000, 10_000):
    cursor.arraysize = cursor.prefetchrows = size
    start = time.perf_counter()
    count = sum(1 for _ in cursor.execute("SELECT * FROM big"))
    print(f"  arraysize {size:>6}: {time.perf_counter() - start:7.3f} s ({count:,} linhas)")

# batcherrors: o lote não para no primeiro erro
cursor.execute("DROP TABLE big PURGE")
cursor.execute("CREATE TABLE big (id NUMBER PRIMARY KEY, v VARCHAR2(5))")
cursor.executemany("INSERT INTO big VALUES (:1, :2)", [(1, "ok"), (2, "valor_grande_demais"), (3, "ok"), (1, "dup")], batcherrors=True)
for error in cursor.getbatcherrors():
    print(f"  linha {error.offset} do lote recusada: {error.message.splitlines()[0][:60]}")
conn.commit()
cursor.execute("SELECT COUNT(*) FROM big")
print("  linhas boas gravadas:", cursor.fetchone()[0])
cursor.execute("DROP TABLE big PURGE")
conn.close()

# pool
start = time.perf_counter()
for _ in range(20):
    oracledb.connect(**ORACLE).close()
connect = (time.perf_counter() - start) / 20
pool = oracledb.create_pool(min=2, max=5, **ORACLE)
start = time.perf_counter()
for _ in range(500):
    with pool.acquire():
        pass
acquire = (time.perf_counter() - start) / 500
pool.close()
print(f"conexão nova: {connect * 1e3:.1f} ms | do pool: {acquire * 1e6:.0f} us ({connect / acquire:,.0f}x)")
