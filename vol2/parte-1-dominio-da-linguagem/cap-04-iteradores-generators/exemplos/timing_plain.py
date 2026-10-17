"""Tempos sem tracemalloc (ele distorce): 10 milhoes."""
import time

N = 10_000_000
for name, fn in [("lista", lambda: sum([n * 2 for n in range(N)])),
                 ("gerador", lambda: sum(n * 2 for n in range(N)))]:
    start = time.perf_counter()
    fn()
    print(name, round(time.perf_counter() - start, 2), "s")
