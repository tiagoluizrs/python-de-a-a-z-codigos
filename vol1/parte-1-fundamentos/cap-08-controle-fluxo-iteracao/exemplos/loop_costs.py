"""Custo de formas diferentes de percorrer dados."""
import sys
import timeit
import tracemalloc

N = 1_000_000
data = list(range(N))


def index_loop():
    total = 0
    for i in range(len(data)):
        total += data[i]
    return total


def direct_loop():
    total = 0
    for value in data:
        total += value
    return total


def enumerate_loop():
    total = 0
    for i, value in enumerate(data):
        total += value
    return total


def while_loop():
    total = 0
    i = 0
    n = len(data)
    while i < n:
        total += data[i]
        i += 1
    return total


def comprehension_then_sum():
    return sum([value for value in data])


def generator_sum():
    return sum(value for value in data)


def builtin_sum():
    return sum(data)


candidates = [index_loop, direct_loop, enumerate_loop, while_loop,
              comprehension_then_sum, generator_sum, builtin_sum]
assert len({f() for f in candidates}) == 1

print(f"somando {N:,} inteiros (melhor de 5, em ms)")
for func in candidates:
    best = min(timeit.repeat(func, number=1, repeat=5))
    print(f"{func.__name__:24s} {best * 1000:7.1f}")

# memoria: lista x expressao geradora x range
print("\nmemoria do conteiner:")
print("list(range(N)):", sys.getsizeof(list(range(N))), "bytes")
print("range(N):", sys.getsizeof(range(N)), "bytes")
print("gerador:", sys.getsizeof(n for n in range(N)), "bytes")

tracemalloc.start()
total = sum([n * 2 for n in range(N)])
_, peak_list = tracemalloc.get_traced_memory()
tracemalloc.reset_peak()
tracemalloc.stop()

tracemalloc.start()
total = sum(n * 2 for n in range(N))
_, peak_gen = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"pico com lista:   {peak_list / 1e6:8.1f} MB")
print(f"pico com gerador: {peak_gen / 1e3:8.1f} KB")
