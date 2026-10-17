"""SQLite com asyncio: aiosqlite (uma thread por conexão) e to_thread."""
import asyncio
import sqlite3
import time

import aiosqlite


def slow_query():
    conn = sqlite3.connect(":memory:")
    # toda a carga acontece DENTRO do SQLite (CTE recursiva): o GIL fica solto durante a execução
    total = conn.execute("WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c WHERE x < 1500000) SELECT SUM(x * x) FROM c").fetchone()[0]
    conn.close()
    return total


async def main():
    async with aiosqlite.connect(":memory:") as db:
        await db.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
        await db.executemany("INSERT INTO t (name) VALUES (?)", [("a",), ("b",), ("c",)])
        await db.commit()
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM t ORDER BY id") as cursor:
            print("async for:", [dict(row) async for row in cursor])

    # sqlite3 comum em um laço asyncio: to_thread, e a conexão nasce DENTRO da thread
    start = time.perf_counter()
    results = await asyncio.gather(*(asyncio.to_thread(slow_query) for _ in range(4)))
    print(f"4 consultas pesadas via to_thread: {time.perf_counter() - start:.2f} s | iguais: {len(set(results)) == 1}")
    start = time.perf_counter()
    for _ in range(4):
        slow_query()
    print(f"as mesmas 4 em sequência       : {time.perf_counter() - start:.2f} s (o sqlite3 solta o GIL enquanto o SQLite trabalha: consultas pesadas em threads rodam em paralelo)")


asyncio.run(main())
