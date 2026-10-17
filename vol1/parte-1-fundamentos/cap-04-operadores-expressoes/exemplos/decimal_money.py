"""Decimal: aritmética decimal exata (e controle de arredondamento)."""
from decimal import ROUND_HALF_UP, Decimal, getcontext

print(0.1 + 0.2)                              # 0.30000000000000004
print(Decimal("0.1") + Decimal("0.2"))        # 0.3
print(Decimal(0.1))                           # o float, exato: 0.1000000000000000055...

price = Decimal("19.99")
total = price * 3
print(total, total.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))   # 59.97 60.0
print(Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))  # 2.68
print(getcontext().prec)                      # 28 dígitos significativos por padrão
