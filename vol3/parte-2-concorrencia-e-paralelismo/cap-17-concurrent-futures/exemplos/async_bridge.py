"""A ponte com o asyncio: executar código bloqueante sem travar o laço."""
import asyncio
import concurrent.futures as cf
import time

import tasks


async def main():
    loop = asyncio.get_running_loop()
    start = time.perf_counter()
    results = await asyncio.gather(*(loop.run_in_executor(None, tasks.slow, 0.2) for _ in range(5)))
    print(f"5 esperas de 0,2 s bloqueantes via run_in_executor(None, ...): {time.perf_counter() - start:.2f} s")

    with cf.ProcessPoolExecutor(2) as pool:
        value = await loop.run_in_executor(pool, tasks.cpu_sum, 100_000)
    print("CPU em um ProcessPoolExecutor, sem travar o laço:", value)

    start = time.perf_counter()
    await asyncio.gather(*(asyncio.to_thread(tasks.slow, 0.2) for _ in range(5)))
    print(f"asyncio.to_thread (atalho para o executor padrão): {time.perf_counter() - start:.2f} s")


if __name__ == "__main__":
    asyncio.run(main())
