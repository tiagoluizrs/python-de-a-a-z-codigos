"""psycopg assíncrono: conexão, pool e concorrência (e a pegadinha do laço no Windows)."""
import asyncio
import sys
import time

import psycopg
from psycopg_pool import AsyncConnectionPool

from pgenv import DSN


async def main():
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        cursor = await conn.execute("SELECT 1 + 1")
        print("conexão assíncrona:", await cursor.fetchone())

    async with AsyncConnectionPool(DSN, min_size=2, max_size=10, open=False) as pool:
        await pool.wait()

        async def one(i):
            async with pool.connection() as conn:
                cursor = await conn.execute("SELECT pg_sleep(0.1), %s::int AS i", (i,))
                return (await cursor.fetchone())[1]

        start = time.perf_counter()
        results = await asyncio.gather(*(one(i) for i in range(20)))
        print(f"20 consultas de 0,1 s, pool de 10: {time.perf_counter() - start:.2f} s | ordem preservada: {results == list(range(20))}")

        start = time.perf_counter()
        async with asyncio.TaskGroup() as group:
            for i in range(10):
                group.create_task(one(i))
        print(f"10 consultas de 0,1 s com TaskGroup: {time.perf_counter() - start:.2f} s (cabem no pool: 1 rodada)")

    # cursor com 'async for': sem carregar tudo
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        async with conn.cursor(name="stream") as cursor:
            await cursor.execute("SELECT generate_series(1, 50000)")
            total = 0
            async for (value,) in cursor:
                total += value
        print("soma por cursor assíncrono de servidor:", total)


if sys.platform == "win32":
    print("Windows: o psycopg assíncrono NÃO funciona com o ProactorEventLoop padrão; use loop_factory=asyncio.SelectorEventLoop (Capítulo 18 do Volume 3)")
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
else:
    asyncio.run(main())
