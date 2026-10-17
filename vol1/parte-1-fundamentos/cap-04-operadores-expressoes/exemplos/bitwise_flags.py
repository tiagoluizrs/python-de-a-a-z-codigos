"""Operadores bit a bit: máscaras, permissões e truques."""
READ, WRITE, EXECUTE = 0b001, 0b010, 0b100

permissions = READ | WRITE          # liga bits
print(f"{permissions:03b}")         # 011
print(bool(permissions & WRITE))    # True: testa o bit
permissions &= ~WRITE               # desliga o bit
print(f"{permissions:03b}")         # 001
permissions ^= EXECUTE              # inverte o bit
print(f"{permissions:03b}")         # 101

x, y = 0b1010, 0b1100
print(x & y, x | y, x ^ y, ~x, x << 1, y >> 2)   # 8 14 6 -11 20 3
print(~5 == -5 - 1)                 # True: ~x == -x - 1 (complemento de dois)
print(-1 >> 10, -8 >> 1)            # -1 -4: o deslocamento preserva o sinal
print((1 << 70) | 1)                # funciona com inteiros gigantes

n = 40
print(n & (n - 1) == 0, 64 & (64 - 1) == 0)   # False True: potência de dois?
print(n & 1 == 0)                   # True: (n & 1) == 0; diferente do C!
print((255).bit_count(), bin(n), f"{n:#010b}")

# Os mesmos símbolos em outros tipos
print({1, 2, 3} | {3, 4}, {1, 2, 3} & {2, 3, 4}, {1, 2, 3} - {2}, {1, 2} ^ {2, 3})
print({"a": 1} | {"b": 2, "a": 9})  # união de dicionários (3.9+): a direita vence
