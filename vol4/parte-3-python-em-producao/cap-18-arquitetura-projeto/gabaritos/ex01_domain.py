"""Gabarito do exercício 1."""
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from functools import total_ordering

CENT = Decimal("0.01")


class DomainError(Exception):
    pass


@total_ordering
class Money:
    __slots__ = ("_amount",)

    def __init__(self, value):
        if isinstance(value, float):
            raise TypeError("use str, int ou Decimal: float já chega impreciso")
        try:
            self._amount = Decimal(value).quantize(CENT, rounding=ROUND_HALF_EVEN)
        except InvalidOperation:
            raise ValueError(f"valor inválido: {value!r}") from None

    @property
    def amount(self):
        return self._amount

    def __add__(self, other):
        return Money(self._amount + other._amount)

    def __sub__(self, other):
        return Money(self._amount - other._amount)

    def __mul__(self, factor):
        if isinstance(factor, float):
            raise TypeError("fator float não aceito")
        return Money(self._amount * Decimal(factor))

    __rmul__ = __mul__

    def __eq__(self, other):
        return isinstance(other, Money) and self._amount == other._amount

    def __lt__(self, other):
        return self._amount < other._amount

    def __hash__(self):
        return hash(self._amount)

    def __str__(self):
        return "R$ " + f"{self._amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def __repr__(self):
        return f"Money('{self._amount}')"


@dataclass
class Cart:
    items: dict = field(default_factory=dict)
    coupon: tuple | None = None
    status: str = "open"

    def _require_open(self):
        if self.status != "open":
            raise DomainError(f"carrinho {self.status}")

    def add(self, sku, qty, unit_price):
        self._require_open()
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise DomainError("quantidade deve ser um inteiro positivo")
        current = self.items.get(sku, (0, unit_price))[0]
        if current + qty > 10:
            raise DomainError(f"no máximo 10 unidades de {sku}")
        if sum(q for q, _ in self.items.values()) + qty > 30:
            raise DomainError("no máximo 30 unidades no carrinho")
        self.items[sku] = (current + qty, unit_price)

    def remove(self, sku, qty=None):
        self._require_open()
        if sku not in self.items:
            raise DomainError(f"{sku} não está no carrinho")
        current, price = self.items[sku]
        if qty is None or qty == current:
            del self.items[sku]
        elif qty > current:
            raise DomainError(f"só há {current} de {sku}")
        else:
            self.items[sku] = (current - qty, price)

    def apply_coupon(self, code, percent):
        self._require_open()
        if self.coupon is not None:
            raise DomainError("só um cupom por carrinho")
        if not Decimal("0") < percent <= Decimal("0.30"):
            raise DomainError("desconto deve ficar entre 0 e 30%")
        self.coupon = (code, percent)

    def subtotal(self):
        total = Money(0)
        for qty, price in self.items.values():
            total = total + price * qty
        return total

    def total(self):
        sub = self.subtotal()
        return sub - sub * self.coupon[1] if self.coupon else sub

    def checkout(self):
        self._require_open()
        if not self.items:
            raise DomainError("carrinho vazio")
        if self.total() < Money("10.00"):
            raise DomainError("pedido mínimo de R$ 10,00")
        self.status = "closed"
