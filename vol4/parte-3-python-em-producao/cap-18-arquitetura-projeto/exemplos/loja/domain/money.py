"""Dinheiro como valor: Decimal com duas casas, imutável, sem dependências de nada."""
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

CENT = Decimal("0.01")


@dataclass(frozen=True, order=True)
class Money:
    amount: Decimal

    def __init__(self, amount):
        object.__setattr__(self, "amount", Decimal(str(amount)).quantize(CENT, rounding=ROUND_HALF_EVEN))

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        return Money(self.amount - other.amount)

    def __mul__(self, factor) -> "Money":
        return Money(self.amount * Decimal(str(factor)))

    __rmul__ = __mul__

    def __str__(self) -> str:
        return f"R$ {self.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


ZERO = Money(0)
