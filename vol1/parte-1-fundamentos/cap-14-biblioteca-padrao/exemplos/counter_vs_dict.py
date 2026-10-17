"""Medição: contar ocorrências com dict manual, defaultdict e Counter."""
import random
import timeit
from collections import Counter, defaultdict

random.seed(42)
words = [f"w{random.randrange(1000)}" for _ in range(200_000)]


def manual():
    counts = {}
    for w in words:
        if w in counts:
            counts[w] += 1
        else:
            counts[w] = 1
    return counts


def with_get():
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts


def with_defaultdict():
    counts = defaultdict(int)
    for w in words:
        counts[w] += 1
    return counts


def with_counter():
    return Counter(words)


assert manual() == with_get() == dict(with_defaultdict()) == with_counter()
for fn in (manual, with_get, with_defaultdict, with_counter):
    best = min(timeit.repeat(fn, number=1, repeat=5))
    print(f"{fn.__name__:17} {best * 1000:6.1f} ms")
