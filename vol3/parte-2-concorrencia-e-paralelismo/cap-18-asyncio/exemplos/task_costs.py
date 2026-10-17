"""Quanto custa uma tarefa assíncrona (e por que milhares são viáveis)."""
import asyncio
import threading
import time
import tracemalloc


async def noop():
    pass


async def idle(event):
    await event.wait()


async def main():
    n = 100_000
    start = time.perf_counter()
    await asyncio.gather(*(noop() for _ in range(n)))
    print(f"gather de {n:,} corrotinas vazias        : {(time.perf_counter() - start) / n * 1e6:5.2f} us cada")

    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for _ in range(n):
            tg.create_task(noop())
    print(f"TaskGroup com {n:,} tarefas              : {(time.perf_counter() - start) / n * 1e6:5.2f} us cada")

    loop = asyncio.get_running_loop()
    loop.set_task_factory(asyncio.eager_task_factory)
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for _ in range(n):
            tg.create_task(noop())
    print(f"mesmo, com eager_task_factory            : {(time.perf_counter() - start) / n * 1e6:5.2f} us cada (começa a rodar já no create_task)")
    loop.set_task_factory(None)

    # memória por tarefa parada
    event = asyncio.Event()
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    tasks = [asyncio.create_task(idle(event)) for _ in range(10_000)]
    await asyncio.sleep(0)
    used = tracemalloc.get_traced_memory()[0] - before
    tracemalloc.stop()
    print(f"10.000 tarefas esperando: ~{used / 10_000:,.0f} bytes cada ({used / 1e6:.1f} MB no total)")
    event.set()
    await asyncio.gather(*tasks)

    # comparação com threads (Capítulo 15)
    start = time.perf_counter()
    stop = threading.Event()
    threads = [threading.Thread(target=stop.wait) for _ in range(1_000)]
    for t in threads:
        t.start()
    elapsed = time.perf_counter() - start
    stop.set()
    for t in threads:
        t.join()
    print(f"1.000 threads esperando: criar levou {elapsed / 1_000 * 1e6:.0f} us cada")


asyncio.run(main())
