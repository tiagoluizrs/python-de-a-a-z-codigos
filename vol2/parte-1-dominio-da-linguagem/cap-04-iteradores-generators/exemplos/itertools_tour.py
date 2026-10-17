"""itertools a fundo."""
import sys
from itertools import (accumulate, batched, chain, combinations, count,
                       dropwhile, groupby, islice, pairwise, permutations,
                       product, repeat, starmap, takewhile, tee,
                       zip_longest)
import operator

print(list(islice(count(), 3)), list(islice("ABCDEFG", 1, 6, 2)))
try:
    islice("abc", -1)
except ValueError as exc:
    print("ValueError:", exc)

nums = [1, 3, 5, 6, 7, 9]
print(list(takewhile(lambda n: n % 2, nums)))
print(list(dropwhile(lambda n: n % 2, nums)))
# takewhile consome o primeiro item que falha
it = iter(nums)
print(list(takewhile(lambda n: n < 5, it)), list(it))

print(list(accumulate([1, 2, 3, 4])))
print(list(accumulate([1, 2, 3, 4], operator.mul)))
print(list(accumulate([3, 1, 4, 1, 5], max)))
print(list(accumulate([100, -30, 20], initial=1000)))

rows = [[1, 2], [3], [], [4]]
print(list(chain.from_iterable(rows)))

# chain.from_iterable aceita iterador de iteraveis (preguicoso)
print(list(islice(chain.from_iterable(repeat([0, 1])), 5)))

print(list(product("ab", [1, 2])))
print(len(list(product(range(10), repeat=3))))
print(list(permutations("abc", 2)))
print(list(combinations("abcd", 2)))
print(len(list(permutations(range(8)))))

print(list(zip_longest("ab", [1, 2, 3], fillvalue="-")))
print(list(batched("ABCDEFG", 3)))
try:
    list(batched("ABCDEFG", 3, strict=True))
except ValueError as exc:
    print("ValueError:", exc)
try:
    list(zip("ab", [1, 2, 3], strict=True))
except ValueError as exc:
    print("ValueError:", exc)

print(list(starmap(pow, [(2, 3), (3, 2), (10, 0)])))
print(list(map(pow, [2, 3], [3, 2])))
print(list(repeat("x", 3)), list(map(pow, range(4), repeat(2))))

# groupby com chave e consumo no laco
words = sorted(["pear", "fig", "apple", "kiwi", "plum", "date"], key=len)
for size, group in groupby(words, key=len):
    print(size, list(group))

# tee e memoria
a, b = tee(iter(range(5)))
print(next(a), next(a), next(b))
print(list(a), list(b))

big_a, big_b = tee(range(10**6))
for _ in big_a:
    pass     # b nao foi consumido: tee guarda 1 milhao de itens
print(sys.getsizeof(list(range(3))), "(ref.)")
print(next(big_b))

for _ in pairwise([1, 2, 3]):
    pass
