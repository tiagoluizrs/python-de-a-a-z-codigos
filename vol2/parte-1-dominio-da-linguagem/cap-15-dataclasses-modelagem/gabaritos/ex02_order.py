"""Gabarito do exercício 2."""
from dataclasses import dataclass, replace
from decimal import Decimal


@dataclass(frozen=True)
class LineItem:
    sku: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantidade deve ser positiva")

    @property
    def total(self):
        return self.quantity * self.unit_price


@dataclass(frozen=True)
class Order:
    customer: str
    items: tuple = ()

    @property
    def total(self):
        return sum((item.total for item in self.items), Decimal("0"))

    def add(self, item):
        return replace(self, items=self.items + (item,))       # novo objeto
