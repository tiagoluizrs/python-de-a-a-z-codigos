"""bytes, bytearray e memoryview: imutável, mutável e visão sem cópia."""
import sys
import timeit

b = b"hello"
ba = bytearray(b"hello")
ba[0] = ord("J")
ba.extend(b" world")
ba += b"!"
print(b, ba, bytes(ba), ba.decode())
print(sys.getsizeof(b""), sys.getsizeof(b), sys.getsizeof(bytearray()),
      sys.getsizeof(ba))
try:
    b[0] = 74
except TypeError as exc:
    print("TypeError:", exc)
print(b.upper(), b.split(b"l"), b.hex(), bytes.fromhex("48 49"))
print(int.from_bytes(b"\x01\x00", "big"), (258).to_bytes(2, "little"))
print(b"abc" < b"abd", b"%d items" % 3, repr(b"\x00\xffA"))

# memoryview: fatia sem copiar
data = bytes(range(256)) * 4096          # 1 MiB
view = memoryview(data)
chunk = view[1000:2000]
print(len(chunk), chunk.nbytes, chunk[0], chunk.obj is data)
print(sys.getsizeof(chunk), sys.getsizeof(data[1000:2000]))

n = 20000
copy_time = timeit.timeit(lambda: data[1000:600000], number=n)
view_time = timeit.timeit(lambda: view[1000:600000], number=n)
print(f"fatia bytes (copia 600 KB): {copy_time / n * 1e6:8.2f} us")
print(f"fatia memoryview:           {view_time / n * 1e6:8.2f} us")

# escrever através da view altera o bytearray original
buf = bytearray(b"abcdef")
mv = memoryview(buf)
mv[1:3] = b"XY"
print(buf)
mv.release()

# 3.15: take_bytes tira o conteúdo do bytearray sem copiar
if hasattr(bytearray, "take_bytes"):
    out = bytearray(b"payload")
    print(out.take_bytes(), out)
