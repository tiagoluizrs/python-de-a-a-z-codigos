"""A MESMA carga de CPU em quatro executores: só a classe muda."""
import concurrent.futures as cf
import time

import tasks

WORK = [400_000] * 32

if __name__ == "__main__":
    start = time.perf_counter()
    expected = [tasks.cpu_sum(n) for n in WORK]
    base = time.perf_counter() - start
    print(f"sequencial: {base:.2f} s")
    for label, cls in (("ThreadPoolExecutor", cf.ThreadPoolExecutor), ("ProcessPoolExecutor", cf.ProcessPoolExecutor), ("InterpreterPoolExecutor", cf.InterpreterPoolExecutor)):
        start = time.perf_counter()
        with cls(max_workers=8) as pool:
            got = list(pool.map(tasks.cpu_sum, WORK))
        elapsed = time.perf_counter() - start
        assert got == expected
        print(f"  {label:<24}: {elapsed:.2f} s | ganho {base / elapsed:4.1f}x")

    print("E/S (50 esperas de 0,1 s):")
    for label, cls, workers in (("ThreadPoolExecutor(50)", cf.ThreadPoolExecutor, 50), ("ProcessPoolExecutor(8)", cf.ProcessPoolExecutor, 8)):
        start = time.perf_counter()
        with cls(max_workers=workers) as pool:
            list(pool.map(tasks.slow, [0.1] * 50))
        print(f"  {label:<24}: {time.perf_counter() - start:.2f} s")
