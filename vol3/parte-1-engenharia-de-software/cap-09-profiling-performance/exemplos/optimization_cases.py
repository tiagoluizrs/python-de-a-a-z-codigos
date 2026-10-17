"""Seis otimizações com resultado medido: algoritmo e estrutura de dados primeiro."""
import timeit
from collections import Counter


def best(stmt, **ns):
    return min(timeit.repeat(stmt, globals=ns, number=3, repeat=3)) / 3


results = []

# 1) Duplicatas: lista (O(n^2)) x dict (O(n))
data = [i % 1500 for i in range(15_000)]


def slow_unique(items):
    seen = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


results.append(("duplicatas: lista -> dict.fromkeys", best("slow_unique(data)", **globals()), best("list(dict.fromkeys(data))", **globals())))

# 2) Interseção: x in lista x conjunto
a, b = list(range(0, 6_000, 2)), list(range(0, 6_000, 3))
results.append(("interseção: `in` lista -> conjunto", best("[x for x in a if x in b]", **globals()), best("[x for x in a if x in set_b]", set_b=set(b), a=a)))

# 3) Contagem: list.count em laço x Counter
words = ["w%d" % (i % 300) for i in range(6_000)]
results.append(("contagem: count() em laço -> Counter",
                best("{w: words.count(w) for w in set(words)}", **globals()), best("Counter(words)", **globals())))

# 4) Soma de pares: dois laços x dicionário de complementos
nums = list(range(3_000))


def pairs_slow(nums, target):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] + nums[j] == target)


def pairs_fast(nums, target):
    seen, count = Counter(), 0
    for x in nums:
        count += seen[target - x]
        seen[x] += 1
    return count


assert pairs_slow(nums[:300], 150) == pairs_fast(nums[:300], 150)
results.append(("pares com soma alvo: O(n^2) -> O(n)", best("pairs_slow(nums, 3000)", **globals()), best("pairs_fast(nums, 3000)", **globals())))

# 5) Fibonacci recursivo: memoização
from functools import cache


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


@cache
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


results.append(("fib(24): recursão -> @cache", best("fib(24)", **globals()), best("fib_cached.cache_clear(); fib_cached(24)", **globals())))

# 6) Juntar textos: += em laço x join
parts = ["pedaço"] * 5_000
results.append(("concatenar 5 mil textos: += -> join", best("s = ''\nfor p in parts: s += p", **globals()), best("''.join(parts)", **globals())))

print(f"{'caso':<42}{'antes':>10}{'depois':>10}{'ganho':>9}")
for label, before, after in results:
    print(f"{label:<42}{before * 1e3:>8.2f}ms{after * 1e3:>8.3f}ms{before / after:>8.0f}x")

# Geradores: a memória, não o tempo
import tracemalloc

tracemalloc.start()
sum([i * i for i in range(300_000)])
peak_list = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
tracemalloc.start()
sum(i * i for i in range(300_000))
peak_gen = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
print(f"soma de quadrados (300 mil): lista pico {peak_list / 1e6:.2f} MB | gerador pico {peak_gen / 1e6:.4f} MB")
