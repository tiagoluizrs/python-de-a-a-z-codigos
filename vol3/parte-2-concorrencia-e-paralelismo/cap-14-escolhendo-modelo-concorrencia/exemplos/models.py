"""Os modelos de execução, em funções pequenas, para comparar a mesma tarefa."""
import asyncio
import concurrent.futures as cf
import os
import time


def run_sequential(func, items):
    return [func(item) for item in items]


def run_threads(func, items, workers):
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(func, items))


def run_processes(func, items, workers):
    with cf.ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(func, items))


def run_asyncio(func, items):
    async def main():
        return await asyncio.gather(*(asyncio.to_thread(func, item) for item in items))

    return asyncio.run(main())


def run_asyncio_native(coro_func, items):
    async def main():
        return await asyncio.gather(*(coro_func(item) for item in items))

    return asyncio.run(main())


def timed(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return time.perf_counter() - start, result


CPUS = os.cpu_count() or 1
