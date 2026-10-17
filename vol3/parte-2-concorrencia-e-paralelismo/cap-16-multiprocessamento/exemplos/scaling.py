"""O ganho real do multiprocessamento em uma tarefa de CPU."""
import multiprocessing as mp
import time

import tasks

WORK = [400_000] * 64

if __name__ == "__main__":
    start = time.perf_counter()
    expected = [tasks.cpu_sum(n) for n in WORK]
    base = time.perf_counter() - start
    print(f"sequencial: {base:.2f} s ({len(WORK)} tarefas)")
    for processes in (1, 2, 4, 8, 16):
        start = time.perf_counter()
        with mp.Pool(processes) as pool:
            got = pool.map(tasks.cpu_sum, WORK)
        elapsed = time.perf_counter() - start
        assert got == expected
        print(f"  {processes:>2} processos: {elapsed:.2f} s | ganho {base / elapsed:4.1f}x | eficiência {base / elapsed / processes:4.0%}")
    print("o tempo inclui criar e fechar o Pool (~100 a 300 ms).")
