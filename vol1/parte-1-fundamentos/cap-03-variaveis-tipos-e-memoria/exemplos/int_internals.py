"""Como o CPython guarda um int: uma lista de 'dígitos' de 30 bits."""
import sys

print(sys.int_info)

for n in (0, 1, 2**30 - 1, 2**30, 2**60, 2**90, 2**1000):
    label = n if n < 10**6 else f"2**{n.bit_length() - 1}"
    print(f"{label!s:>8}  bits={n.bit_length():>5}  bytes={sys.getsizeof(n):>4}")

# Conversão para bytes: o inteiro "de verdade" em binário
print((1000).to_bytes(2, "big"))             # b'\x03\xe8'
print((1000).to_bytes(4, "little").hex(" ")) # e8 03 00 00
print(int.from_bytes(b"\x03\xe8", "big"))    # 1000
print((255).bit_count())                     # 8 bits ligados

# Limite de conversão texto -> int (proteção contra ataques de negação de serviço)
print(sys.get_int_max_str_digits())          # 4300
try:
    int("9" * 5000)
except ValueError as error:
    print(error)
