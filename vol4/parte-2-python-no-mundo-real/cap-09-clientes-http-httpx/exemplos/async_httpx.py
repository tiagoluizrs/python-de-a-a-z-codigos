"""httpx assíncrono: AsyncClient, gather, limites de concorrência."""
import asyncio
import time

import httpx

from demo_server import serve


async def main(base):
    urls = [f"{base}/slow?d=0.1" for _ in range(50)]

    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        for url in urls[:10]:
            await client.get(url)
        print(f"10 requisições de 0,1 s uma após a outra : {time.perf_counter() - start:.2f} s")

    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=100)) as client:
        start = time.perf_counter()
        responses = await asyncio.gather(*(client.get(url) for url in urls))
        print(f"50 requisições de 0,1 s com gather        : {time.perf_counter() - start:.2f} s | todas 200: {all(r.status_code == 200 for r in responses)}")

    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=5)) as client:
        start = time.perf_counter()
        try:
            await asyncio.gather(*(client.get(url, timeout=httpx.Timeout(5.0, pool=0.15)) for url in urls[:20]))
        except httpx.PoolTimeout:
            print(f"20 requisições com max_connections=5 e pool=0,15 s -> PoolTimeout em {time.perf_counter() - start:.2f} s (esperar uma conexão livre também tem prazo)")

    semaphore = asyncio.Semaphore(10)

    async def limited(client, url):
        async with semaphore:                                     # no máximo 10 ao mesmo tempo (educado com o servidor)
            return await client.get(url)

    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(limited(client, url)) for url in urls]
        print(f"50 requisições com Semaphore(10)          : {time.perf_counter() - start:.2f} s (5 rodadas de 0,1 s) | ordem preservada: {[t.result().json()['slept'] for t in tasks][:3]}...")

    # erros isolados: gather(return_exceptions=True) não derruba os outros
    async with httpx.AsyncClient(base_url=base, timeout=0.3) as client:
        results = await asyncio.gather(client.get("/json"), client.get("/slow", params={"d": 1}), client.get("/status/500"), return_exceptions=True)
        print("\nresultados misturados:", [r.status_code if isinstance(r, httpx.Response) else type(r).__name__ for r in results])


with serve() as base:
    asyncio.run(main(base))
    print("\no Client síncrono NÃO é seguro para várias corrotinas aguardando; use AsyncClient (um por aplicação) e compartilhe-o entre tarefas.")
