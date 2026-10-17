"""O custo por tarefa: submit/map em threads e processos, e o chunksize do ProcessPoolExecutor."""
import concurrent.futures as cf
import time

import tasks

N = 10_000

if __name__ == "__main__":
    start = time.perf_counter()
    for i in range(N):
        tasks.square(i)
    print(f"{N:,} chamadas diretas                    : {(time.perf_counter() - start) * 1e3:7.1f} ms")

    with cf.ThreadPoolExecutor(4) as pool:
        start = time.perf_counter()
        list(pool.map(tasks.square, range(N)))
        print(f"ThreadPoolExecutor.map                  : {(time.perf_counter() - start) * 1e3:7.1f} ms ({(time.perf_counter() - start) / N * 1e6:.1f} us por tarefa)")
        start = time.perf_counter()
        futures = [pool.submit(tasks.square, i) for i in range(N)]
        [f.result() for f in futures]
        print(f"ThreadPoolExecutor.submit + result      : {(time.perf_counter() - start) * 1e3:7.1f} ms")

    with cf.ProcessPoolExecutor(4) as pool:
        list(pool.map(tasks.square, range(8)))                      # aquece os processos
        for chunksize in (1, 50, 500):
            start = time.perf_counter()
            list(pool.map(tasks.square, range(N), chunksize=chunksize))
            print(f"ProcessPoolExecutor.map chunksize={chunksize:<4}   : {(time.perf_counter() - start) * 1e3:7.1f} ms")
        start = time.perf_counter()
        list(pool.map(tasks.apply_batch, [tasks.square] * 20, [list(range(i * 500, (i + 1) * 500)) for i in range(20)]))
        print(f"ProcessPoolExecutor, 20 lotes de 500 (manual): {(time.perf_counter() - start) * 1e3:7.1f} ms")
