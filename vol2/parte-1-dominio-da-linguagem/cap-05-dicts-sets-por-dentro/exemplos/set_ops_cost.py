"""Custo das operações de conjunto: depende do operando que você copia."""
import timeit

big = set(range(100_000))
small = set(range(10))

for label in ("big | small", "big & small", "small & big",
              "big - small", "small - big", "big.isdisjoint(small)",
              "big | big"):
    seconds = min(timeit.repeat(label, globals=globals(),
                                number=100, repeat=3)) / 100
    print(f"{label:<24}{seconds * 1e6:10.1f} us")
