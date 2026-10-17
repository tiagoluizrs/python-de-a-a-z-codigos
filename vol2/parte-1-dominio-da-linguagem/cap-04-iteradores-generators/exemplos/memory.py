"""Lista de 10 milhoes x gerador: memoria e tempo."""
import sys
import time
import tracemalloc

N = 10_000_000


def peak(fn):
    tracemalloc.start()
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    _, top = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, top, elapsed


def with_list():
    return sum([n * 2 for n in range(N)])


def with_gen():
    return sum(n * 2 for n in range(N))


for name, fn in [("lista", with_list), ("gerador", with_gen)]:
    result, top, elapsed = peak(fn)
    print(f"{name:8} pico={top / 1e6:10.3f} MB  tempo={elapsed:.2f}s"
          f"  resultado={result}")

print(sys.getsizeof(n * 2 for n in range(N)), "bytes: o gerador")
big = [n * 2 for n in range(N)]
print(sys.getsizeof(big) / 1e6, "MB so da lista de ponteiros")
