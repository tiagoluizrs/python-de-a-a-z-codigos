"""aiomysql: conexão e pool com asyncio."""
import asyncio
import sys
import time

import aiomysql

import mysqlenv


async def main():
    host, port = mysqlenv.SERVERS[mysqlenv.server_name()]
    async with aiomysql.create_pool(host=host, port=port, user="root", password="root", db="livro", minsize=2, maxsize=10, autocommit=True) as pool:
        async def one(i):
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute("SELECT SLEEP(0.1), %s AS i", (i,))
                    return (await cursor.fetchone())["i"]

        start = time.perf_counter()
        results = await asyncio.gather(*(one(i) for i in range(20)))
        print(f"20 consultas de 0,1 s, pool de 10: {time.perf_counter() - start:.2f} s | ordem preservada: {results == list(range(20))}")


if sys.platform == "win32":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
else:
    asyncio.run(main())
