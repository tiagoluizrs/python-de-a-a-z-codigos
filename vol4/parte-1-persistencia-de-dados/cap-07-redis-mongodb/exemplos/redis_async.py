"""redis.asyncio: o mesmo cliente, com await; e fakeredis para testes sem servidor."""
import asyncio
import time

import redis.asyncio as aioredis

from dbenv import REDIS_URL


async def main():
    # o pool padrão LEVANTA MaxConnectionsError quando as tarefas simultâneas passam do limite;
    # BlockingConnectionPool faz as tarefas ESPERAREM uma conexão livre
    pool = aioredis.BlockingConnectionPool.from_url(REDIS_URL, decode_responses=True, max_connections=50)
    r = aioredis.Redis(connection_pool=pool)
    await r.flushdb()
    await r.set("a", 1)
    print("get assíncrono:", await r.get("a"))

    start = time.perf_counter()
    for i in range(1_000):
        await r.set(f"seq{i}", i)
    sequential = time.perf_counter() - start

    start = time.perf_counter()
    await asyncio.gather(*(r.set(f"par{i}", i) for i in range(1_000)))
    concurrent = time.perf_counter() - start

    start = time.perf_counter()
    async with r.pipeline(transaction=False) as pipe:
        for i in range(1_000):
            pipe.set(f"pipe{i}", i)
        await pipe.execute()
    piped = time.perf_counter() - start
    print(f"1.000 SET: await em laço {sequential * 1e3:.0f} ms | gather (50 conexões) {concurrent * 1e3:.0f} ms | pipeline {piped * 1e3:.0f} ms")
    await r.flushdb()
    await r.aclose()


asyncio.run(main())

# para TESTES: fakeredis implementa o protocolo na memória (sem servidor)
import fakeredis

fake = fakeredis.FakeRedis(decode_responses=True)
fake.set("x", 1)
fake.incr("x")
fake.zadd("z", {"ana": 3, "bia": 5})
print("fakeredis:", fake.get("x"), fake.zrevrange("z", 0, -1), "(rápido e sem Docker; mas Lua e módulos têm limites: teste o essencial no Redis de verdade)")
