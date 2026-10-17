"""map, filter, sorted, min/max com key e comparação com compreensões."""
import timeit

words = ["banana", "Apple", "cherry", "date", "Elder"]

m = map(len, words)
print(m, next(m), list(m))          # lazy: iterador de uso único
f = filter(None, [0, 1, "", "a", None, []])
print(list(f))
print(sorted(words), sorted(words, key=str.lower))
print(min(words, key=len), max(words, key=len))
print(sorted(words, key=len, reverse=True))

nums = list(range(1000))
cases = {
    "map(lambda)": lambda: list(map(lambda n: n * 2, nums)),
    "compreensao": lambda: [n * 2 for n in nums],
    "map(str)": lambda: list(map(str, nums)),
    "comp str": lambda: [str(n) for n in nums],
    "filter(lambda)": lambda: list(filter(lambda n: n % 2, nums)),
    "comp if": lambda: [n for n in nums if n % 2],
}
for name, fn in cases.items():
    t = min(timeit.repeat(fn, number=2000, repeat=5)) / 2000
    print(f"{name:16s} {t * 1e6:8.1f} us")
