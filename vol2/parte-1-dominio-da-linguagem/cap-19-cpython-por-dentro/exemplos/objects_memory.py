"""Objetos por dentro: cabeçalho, strings, internamento e objetos imortais."""
import sys

# Tamanho dos objetos (inclui o cabeçalho: contagem de referências e tipo)
for value in (0, 1, 2**30, 2**60, 2**100):
    print(f"int {value!r:>25} -> {sys.getsizeof(value)} bytes")
print("float:", sys.getsizeof(1.5), "| bool:", sys.getsizeof(True), "| None:", sys.getsizeof(None))
print("list vazia:", sys.getsizeof([]), "| tuple vazia:", sys.getsizeof(()), "| dict vazio:", sys.getsizeof({}))
print("objeto simples:", sys.getsizeof(object()))

# Strings (PEP 393): 1, 2 ou 4 bytes por caractere conforme o MAIOR ponto de código
for label, text in [("ascii", "a" * 10), ("latin-1", "\u00e7" * 10), ("BMP", "\u4e2d" * 10), ("fora do BMP", "\U0001F600" * 10)]:
    print(f"str {label:<12} 10 caracteres -> {sys.getsizeof(text)} bytes")
print("overhead da str vazia:", sys.getsizeof(""))

# Objetos imortais (PEP 683, 3.12): a contagem de referências deles não muda
print("refcount de None:", sys.getrefcount(None), "| de 0:", sys.getrefcount(0))
x = object()
before = sys.getrefcount(x)
y = x
print("objeto comum: ", before, "->", sys.getrefcount(x))

# Internamento: strings "parecidas com identificadores" são compartilhadas
a = "hello_world"
b = "hello_world"
print("mesma constante no mesmo código:", a is b)
c = "".join(["hello", "_", "world"])
print("construída em tempo de execução:", c is a, "| intern:", sys.intern(c) is sys.intern(a))

# Inteiros pequenos são compartilhados
n1 = int("5")
n2 = int("5")
m1 = int("5000")
m2 = int("5000")
print("5 is 5:", n1 is n2, "| 5000 is 5000:", m1 is m2)

# Identidade = endereço de memória (no CPython)
obj = object()
address = int(repr(obj).split("0x")[1].rstrip(">"), 16)
print("id é o endereço de memória:", address == id(obj))
