"""Gabarito do exercício 6."""
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def format_brl(value: int | float | str | Decimal, symbol: bool = True) -> str:
    # str() evita o erro binário do float: Decimal(2.675) != Decimal("2.675")
    amount = value if isinstance(value, Decimal) else Decimal(str(value))
    amount = amount.quantize(CENT, rounding=ROUND_HALF_UP)
    negative = amount < 0          # depois de arredondar: -0.001 vira 0.00
    whole, cents = f"{abs(amount):.2f}".split(".")
    # formata em estilo americano e troca os separadores por um intermediário
    groups = f"{int(whole):,}".replace(",", ".")
    prefix = "R$ " if symbol else ""
    return f"{'-' if negative else ''}{prefix}{groups},{cents}"
