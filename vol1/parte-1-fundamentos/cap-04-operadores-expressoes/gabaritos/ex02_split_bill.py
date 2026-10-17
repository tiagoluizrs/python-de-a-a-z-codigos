"""Gabarito do exercício 2."""
from decimal import Decimal


def split_bill(total: Decimal, people: int) -> list[Decimal]:
    cents = int(total * 100)                 # trabalha em centavos inteiros
    base, extra = divmod(cents, people)      # 'extra' pessoas pagam 1 centavo a mais
    return [Decimal(base + (1 if i < extra else 0)) / 100 for i in range(people)]
