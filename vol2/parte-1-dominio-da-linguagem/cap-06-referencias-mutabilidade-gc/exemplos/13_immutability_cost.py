"""Imutabilidade e custo: strings, tuplas, memoryview."""
import sys
import timeit

# 1) Concatenar texto em laço
def concat_plus(n: int) -> str:
    out = ""
    for i in range(n):
        out += "x"
    return out


def concat_join(n: int) -> str:
    return "".join(["x" for _ in range(n)])


def concat_plus_aliased(n: int) -> str:
    out = ""
    for i in range(n):
        previous = out       # segunda referência: impede o atalho
        out += "x"
    return out


for n in (10_000, 20_000, 40_000):
    t1 = timeit.timeit(lambda: concat_plus(n), number=5) / 5
    t2 = timeit.timeit(lambda: concat_join(n), number=5) / 5
    t3 = timeit.timeit(lambda: concat_plus_aliased(n), number=5) / 5
    print(f"n={n:>6}  += {t1 * 1e3:6.2f} ms   join {t2 * 1e3:6.2f} ms"
          f"   += com alias {t3 * 1e3:7.2f} ms")

# 2) Tuplas: cada concatenação cria outra
t = ()
ids = set()
for i in range(5):
    t += (i,)
    ids.add(id(t))
print("\nobjetos tupla distintos em 5 +=:", len(ids))

# 3) memoryview: fatiar sem copiar
data = bytes(range(256)) * 4000          # ~1 MB
view = memoryview(data)
cut_copy = timeit.timeit(lambda: data[1000:900_000], number=200) / 200
cut_view = timeit.timeit(lambda: view[1000:900_000], number=200) / 200
print(f"\nfatia de bytes     : {cut_copy * 1e6:8.1f} us (copia 900 KB)")
print(f"fatia de memoryview: {cut_view * 1e6:8.1f} us (cópia zero)")
print("mesmo buffer:", view[1000:2000].obj is data)

buf = bytearray(b"hello world")
mv = memoryview(buf)
mv[0:5] = b"HELLO"                       # escreve no buffer original
print(buf)
try:
    bytes_view = memoryview(b"abc")
    bytes_view[0] = 1
except TypeError as exc:
    print("TypeError:", exc)
print("getsizeof(memoryview):", sys.getsizeof(view))
