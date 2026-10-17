"""O float é um IEEE 754 de 64 bits: 1 bit de sinal, 11 de expoente, 52 de mantissa."""
import math
import struct
import sys

print(sys.float_info)

value = 0.1
raw = struct.pack(">d", value)          # os 8 bytes reais
print(raw.hex(" "))                     # 3f b9 99 99 99 99 99 9a
bits = int.from_bytes(raw, "big")
print(f"{bits:064b}")
print(value.hex())                      # 0x1.999999999999ap-4
print(value.as_integer_ratio())         # fração exata armazenada
print(f"{value:.30f}")                  # 0.100000000000000005551115123126

print(0.1 + 0.2 == 0.3)                 # False
print(0.1 + 0.2)                        # 0.30000000000000004
print(math.isclose(0.1 + 0.2, 0.3))     # True: compare com tolerância

print(math.ulp(1.0))                    # 2.220446049250313e-16 (distância ao próximo float)
print(float(2**53) + 1 == float(2**53)) # True: acima de 2**53 faltam inteiros
print(float("nan") == float("nan"))     # False: NaN nunca é igual a nada
