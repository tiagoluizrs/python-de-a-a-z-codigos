"""InterpreterPoolExecutor ao lado dos outros executores, no build com GIL."""
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
        for workers in (4, 8):
            start = time.perf_counter()
            with cls(max_workers=workers) as pool:
                got = list(pool.map(tasks.cpu_sum, WORK))
            elapsed = time.perf_counter() - start
            assert got == expected
            print(f"  {label:<24} {workers} trabalhadores: {elapsed:.2f} s | ganho {base / elapsed:4.1f}x")

    # custo de partida: executor novo, uma tarefa
    for label, cls in (("ProcessPoolExecutor", cf.ProcessPoolExecutor), ("InterpreterPoolExecutor", cf.InterpreterPoolExecutor)):
        start = time.perf_counter()
        with cls(max_workers=4) as pool:
            list(pool.map(tasks.cpu_sum, [10] * 4))
        print(f"  partida + 4 tarefas mínimas, {label:<24}: {(time.perf_counter() - start) * 1e3:6.0f} ms")
