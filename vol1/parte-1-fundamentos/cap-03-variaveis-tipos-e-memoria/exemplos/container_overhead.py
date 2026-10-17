"""Uma lista guarda ponteiros; cada int é um objeto separado. O array guarda os valores crus."""
import tracemalloc
from array import array

N = 1_000_000


def measure(factory):
    tracemalloc.start()
    obj = factory()
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, obj


list_bytes, _keep1 = measure(lambda: list(range(N)))
array_bytes, _keep2 = measure(lambda: array("q", range(N)))

print(f"list  of {N:,} ints : {list_bytes / 1e6:6.1f} MB")
print(f"array of {N:,} ints : {array_bytes / 1e6:6.1f} MB")
print(f"ratio                 : {list_bytes / array_bytes:.1f}x")

# Crescimento da lista: capacidade reservada além do necessário
import sys

items = []
last = sys.getsizeof(items)
print(f"len=0 size={last}")
for i in range(1, 41):
    items.append(i)
    size = sys.getsizeof(items)
    if size != last:
        print(f"len={i:<3} size={size}  (capacity={(size - 56) // 8})")
        last = size
