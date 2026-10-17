"""Tamanho em bytes e tempo de busca: dict, set, list, tuple."""
import sys
import timeit
import tracemalloc

# 1. Tamanho do contêiner (sem contar os objetos apontados)
print("itens   list    tuple     set    dict")
for n in (0, 1, 5, 6, 100, 1000, 100_000):
    lst = list(range(n))
    print(f"{n:>7} {sys.getsizeof(lst):>6} {sys.getsizeof(tuple(lst)):>8}"
          f" {sys.getsizeof(set(lst)):>7}"
          f" {sys.getsizeof(dict.fromkeys(lst)):>7}")

# 2. Memória real (contêiner + objetos) com tracemalloc


def measure(builder):
    tracemalloc.start()
    obj = builder()
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, obj


N = 100_000
keys = [f"key{i}" for i in range(N)]       # as strings ficam fora da conta
dict_bytes, _ = measure(lambda: {k: i for i, k in enumerate(keys)})
pairs_bytes, _ = measure(lambda: [(k, i) for i, k in enumerate(keys)])
set_bytes, _ = measure(lambda: set(keys))
list_bytes, _ = measure(lambda: list(keys))
print(f"\n{N} itens (strings das chaves compartilhadas):")
print(f"dict {{k: i}}           : {dict_bytes / 1e6:6.2f} MB")
print(f"lista de tuplas (k, i) : {pairs_bytes / 1e6:6.2f} MB")
print(f"set de chaves          : {set_bytes / 1e6:6.2f} MB")
print(f"lista de chaves        : {list_bytes / 1e6:6.2f} MB")

# 3. Tempo de busca: x in lista x conjunto x dicionário
print("\nbusca de um item AUSENTE (pior caso para a lista):")
for n in (1_000, 10_000, 100_000):
    data = list(range(n))
    as_set = set(data)
    as_dict = dict.fromkeys(data)
    missing = -1
    reps = 200 if n <= 10_000 else 20
    t_list = timeit.timeit(lambda: missing in data, number=reps) / reps
    t_set = timeit.timeit(lambda: missing in as_set, number=20000) / 20000
    t_dict = timeit.timeit(lambda: missing in as_dict, number=20000) / 20000
    print(f"n={n:>7}: list {t_list * 1e6:9.2f} us | "
          f"set {t_set * 1e9:6.1f} ns | dict {t_dict * 1e9:6.1f} ns")

# 4. Construir: set(lista) uma vez compensa quando há muitas buscas
data = list(range(100_000))
build = timeit.timeit(lambda: set(data), number=20) / 20
print(f"\nconstruir set de 100.000 itens: {build * 1e3:.2f} ms")
