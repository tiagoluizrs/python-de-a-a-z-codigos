"""Operadores aritméticos: onde o Python difere do C."""
import math

print(7 / 2, 7 // 2, 7 % 2)          # 3.5 3 1
print(-7 / 2, -7 // 2, -7 % 2)       # -3.5 -4 1   (// arredonda para BAIXO)
print(7 // -2, 7 % -2)               # -4 -1       (o resto tem o sinal do divisor)
print(divmod(-7, 2))                 # (-4, 1)
assert (-7 // 2) * 2 + (-7 % 2) == -7  # a identidade que o Python preserva

print(10 / 2, type(10 / 2))          # 5.0 <class 'float'>: "/" sempre devolve float
print(2 ** 10, 2 ** -1, 2 ** 0.5)    # 1024 0.5 1.4142135623730951
print(-2 ** 2, (-2) ** 2)            # -4 4: ** vem antes do menos unário
print(2 ** 3 ** 2)                   # 512: ** associa da DIREITA para a esquerda
print(pow(3, 200, 13))               # 9: exponenciação modular (rápida, sem números gigantes)

print(math.isqrt(10**30))            # 1000000000000000: raiz inteira, exata
print((10**30) ** 0.5)               # 1000000000000000.0: via float, aproximada

for expression in ("1 / 0", "2.0 ** 10000", "10 % 0"):
    try:
        eval(expression)
    except (ZeroDivisionError, OverflowError) as error:
        print(f"{expression:>14} -> {type(error).__name__}: {error}")
