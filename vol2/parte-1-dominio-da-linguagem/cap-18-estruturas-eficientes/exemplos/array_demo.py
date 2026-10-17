"""array: vetor compacto de números do mesmo tipo."""
import array
import sys
import tracemalloc

a = array.array("d", [1, 2, 3])
print(a, a.typecode, a.itemsize, len(a))
print(array.typecodes)

# Limites por tipo
b = array.array("b", [127])
try:
    b[0] = 128
except OverflowError as error:
    print("OverflowError:", error)
try:
    array.array("i", [1, "a"])
except TypeError as error:
    print("TypeError:", error)

# Bytes e memoryview: sem cópia
raw = a.tobytes()
print(len(raw), array.array("d", raw) == a)
view = memoryview(a)
view[0] = 99.5
print(a[0], view.format, view.itemsize)


# Memória: 1 milhão de floats
def build_list():
    return [float(i) for i in range(1_000_000)]


def build_array():
    return array.array("d", (float(i) for i in range(1_000_000)))


for label, fn in [("list", build_list), ("array('d')", build_array)]:
    tracemalloc.start()
    kept = fn()
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"  {label:<12}{current / 1e6:6.1f} MB")

# Ler um item CRIA um objeto float novo
arr = array.array("d", [1.5])
print(arr[0] is arr[0])

# Fatiar copia (como lista); append amortizado O(1)
arr.extend([2.5, 3.5])
print(arr[1:], arr.tolist())
