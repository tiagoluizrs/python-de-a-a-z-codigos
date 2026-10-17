"""Um tour por itertools: laços sem montar listas."""
from itertools import (batched, chain, count, cycle, groupby,
                       islice, pairwise, product)

print(list(batched("ABCDEFG", 3)))              # 3.12
try:
    list(batched("ABCDEFG", 3, strict=True))    # strict: 3.13
except ValueError as error:
    print("ValueError:", error)

print(list(pairwise([1, 4, 9, 16])))            # 3.10
print([b - a for a, b in pairwise([1, 4, 9, 16])])

print(list(chain([1, 2], (3,), "ab")))
rows = [[1, 2], [3], [4, 5]]
print(list(chain.from_iterable(rows)))

print(list(islice(count(10, 5), 4)))            # infinito + corte
print(list(islice("ABCDEFG", 2, None, 2)))      # fatia de iteravel
colors = cycle(["red", "green"])
print([next(colors) for _ in range(5)])

print(list(product("ab", [1, 2])))
print(len(list(product(range(10), repeat=3))))  # 1000 combinacoes

# groupby agrupa VIZINHOS iguais
text = "aaabbbccaa"
print([(key, len(list(group))) for key, group in groupby(text)])

# armadilha: sem ordenar, o mesmo grupo aparece varias vezes
people = [("SP", "Ana"), ("RJ", "Bia"), ("SP", "Caio")]
for state, group in groupby(people, key=lambda p: p[0]):
    print("sem ordenar:", state, [name for _, name in group])
ordered = sorted(people, key=lambda p: p[0])
for state, group in groupby(ordered, key=lambda p: p[0]):
    print("ordenado:", state, [name for _, name in group])

# armadilha: o grupo e um iterador compartilhado
groups = [group for _, group in groupby("aabb")]
print([list(group) for group in groups])        # tudo vazio!
groups = [list(group) for _, group in groupby("aabb")]
print(groups)

# a chain vs concatenar: sem criar lista intermediaria
big = chain(range(1_000_000), range(1_000_000))
print(sum(1 for _ in big))
