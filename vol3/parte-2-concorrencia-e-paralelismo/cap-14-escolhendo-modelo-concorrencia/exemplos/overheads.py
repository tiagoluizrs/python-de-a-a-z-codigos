"""O custo de COMEÇAR cada tipo de trabalho concorrente."""
import asyncio
import concurrent.futures as cf
import multiprocessing as mp
import threading
import time

import tasks


def noop():
    pass


def timeit_n(fn, n):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n


def start_thread():
    t = threading.Thread(target=noop)
    t.start()
    t.join()


def start_process():
    p = mp.get_context("spawn").Process(target=noop)
    p.start()
    p.join()


async def coroutine_tasks(n):
    async def one():
        return 1

    start = time.perf_counter()
    await asyncio.gather(*(asyncio.create_task(one()) for _ in range(n)))
    return (time.perf_counter() - start) / n


if __name__ == "__main__":
    print(f"criar e esperar 1 thread        : {timeit_n(start_thread, 300) * 1e6:10.0f} us")
    print(f"criar e esperar 1 corrotina/task: {asyncio.run(coroutine_tasks(20_000)) * 1e6:10.1f} us")
    print(f"criar e esperar 1 processo spawn: {timeit_n(start_process, 5) * 1e3:10.0f} ms")

    # Passar dados: o custo de serializar (pickle) ao cruzar processos
    import pickle

    for size in (1_000, 1_000_000, 50_000_000):
        data = bytes(size)
        start = time.perf_counter()
        pickle.loads(pickle.dumps(data))
        print(f"  pickle ida e volta de {size / 1e6:7.3f} MB: {(time.perf_counter() - start) * 1e3:8.2f} ms")

    # Um pool: o custo fixo de criar e a chamada trivial
    start = time.perf_counter()
    with cf.ProcessPoolExecutor(4) as pool:
        list(pool.map(tasks.square, range(4)))
    print(f"ProcessPoolExecutor(4): criar + 4 chamadas triviais + encerrar: {(time.perf_counter() - start) * 1e3:.0f} ms")
    start = time.perf_counter()
    with cf.ThreadPoolExecutor(4) as pool:
        list(pool.map(tasks.square, range(4)))
    print(f"ThreadPoolExecutor(4):  criar + 4 chamadas triviais + encerrar: {(time.perf_counter() - start) * 1e3:.2f} ms")
