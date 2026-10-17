"""Custos medidos: lista x gerador (1 milhao de itens)."""
import timeit
import tracemalloc

N = 1_000_000


def peak(fn):
    tracemalloc.start()
    fn()
    top = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return top


def best(fn, repeat=5):
    return min(timeit.repeat(fn, number=1, repeat=repeat))


cases = {
    "sum(lista)": lambda: sum([n * 2 for n in range(N)]),
    "sum(gerador)": lambda: sum(n * 2 for n in range(N)),
    "primeiro item (lista)": lambda: [n * 2 for n in range(N)][0],
    "primeiro item (gerador)": lambda: next(n * 2 for n in range(N)),
}
for name, fn in cases.items():
    print(f"{name:24} {best(fn) * 1e3:9.4f} ms {peak(fn) / 1e3:10.1f} KB")

data = [n * 2 for n in range(N)]
gen_data = lambda: (n * 2 for n in range(N))
print(f"2 passadas, lista:   {best(lambda: (sum(data), max(data))) * 1e3:.1f} ms")
print(f"2 passadas, gerador: "
      f"{best(lambda: (sum(gen_data()), max(gen_data()))) * 1e3:.1f} ms")
print(f"data[-1]: {best(lambda: data[-1]) * 1e6:.2f} us | len: "
      f"{best(lambda: len(data)) * 1e6:.2f} us")
print(f"for x in lista: {best(lambda: [None for _ in data]) * 1e3:.1f} ms")
