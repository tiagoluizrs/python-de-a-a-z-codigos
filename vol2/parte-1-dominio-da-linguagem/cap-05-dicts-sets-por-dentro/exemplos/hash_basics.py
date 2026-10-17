"""hash(), o contrato com __eq__ e os hashes dos tipos embutidos."""
import sys
from fractions import Fraction

print(sys.hash_info.algorithm, sys.hash_info.modulus)

# 1. Inteiros: o hash e o proprio valor, modulo 2**61 - 1
print(hash(42), hash(-7), hash(2**61 - 2), hash(2**61 - 1), hash(2**61))

# 2. -1 e reservado pela API C para sinalizar erro: vira -2
print(hash(-1), hash(-2), hash(-1) == hash(-2))

# 3. Valores numericos iguais tem hash igual, mesmo de tipos diferentes
print(hash(1) == hash(1.0) == hash(True) == hash(Fraction(1)))
print(hash(0.5) == hash(Fraction(1, 2)))
print({1: "int", 1.0: "float", True: "bool"})

# 4. Coleções: o hash combina o hash dos elementos
print(hash((1, 2)) == hash((1, 2)), hash((1, 2)) == hash((2, 1)))
print(hash(frozenset({1, 2})) == hash(frozenset({2, 1})))
try:
    hash((1, [2]))
except TypeError as exc:
    print("TypeError:", exc)

# 5. None tem hash constante (desde o 3.12); texto e aleatorizado
print(hash(None) == hash(None), hash(None))
print(hash("abc") == hash("abc"))  # estavel DENTRO do processo

# 6. O contrato: a == b implica hash(a) == hash(b); a volta nao vale
print(hash(1) == hash(1.0), hash(2**61 - 1) == hash(0))
print(2**61 - 1 == 0)              # hashes iguais, objetos diferentes
