"""tee guarda em memoria o que um ramo viu e o outro ainda nao."""
import tracemalloc
from itertools import tee

N = 1_000_000


def measure(consume_both_together):
    tracemalloc.start()
    a, b = tee(iter(range(N)))
    if consume_both_together:
        for x, y in zip(a, b):
            pass
    else:
        for x in a:
            pass
        for y in b:
            pass
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak


print(f"em paralelo: {measure(True) / 1e3:10.1f} KB")
print(f"um e depois o outro: {measure(False) / 1e3:10.1f} KB")
