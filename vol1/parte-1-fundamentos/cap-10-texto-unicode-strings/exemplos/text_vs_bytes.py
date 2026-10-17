"""Texto (str) e bytes são tipos diferentes; a ponte é encode/decode."""

text = "café"
data = text.encode("utf-8")

print(type(text), len(text), text)
print(type(data), len(data), data)
print(list(data))                   # cada byte é um int de 0 a 255
print(data.decode("utf-8") == text)

# misturar os dois não funciona (e nunca funcionou em silêncio)
try:
    text + data
except TypeError as exc:
    print("TypeError:", exc)

print("café" == b"caf\xc3\xa9")      # False, sem erro
print(b"abc"[0], b"abc"[0:1])       # indexar bytes dá int; fatiar dá bytes
print(bytes([99, 97, 102]), bytes(3), b"ab" * 2)
print(bytes.fromhex("c3a9").decode("utf-8"), "é".encode().hex(" "))
