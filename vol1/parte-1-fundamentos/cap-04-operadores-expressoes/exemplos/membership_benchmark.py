"""'in' em list é O(n); em set/dict é O(1) em média. Meça!"""
import timeit

N = 100_000
as_list = list(range(N))
as_set = set(as_list)
as_range = range(N)
missing = N + 1                          # pior caso: elemento ausente

for name, container in (("list", as_list), ("set", as_set), ("range", as_range)):
    seconds = min(timeit.repeat(lambda: missing in container, number=200, repeat=3)) / 200
    print(f"{name:<6} {seconds * 1e9:>12,.0f} ns por busca")
