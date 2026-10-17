"""O pedido e as suas regras. Nenhuma importação de banco, HTTP, e-mail ou framework: só Python."""
from dataclasses import dataclass, field
from decimal import Decimal

from loja.domain.events import OrderPlaced
from loja.domain.money import ZERO, Money

MIN_TOTAL = Money("5.00")
MAX_ITEMS = 20
MAX_DISCOUNT = Decimal("0.50")


class DomainError(Exception):
    """Uma regra de negócio foi violada (um erro ESPERADO, que o chamador mostra ao usuário)."""


@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int
    unit_price: Money

    def subtotal(self) -> Money:
        return self.unit_price * self.qty


@dataclass(frozen=True)
class Coupon:
    code: str
    percent: Decimal                     # 0.10 = 10%

    def __post_init__(self):
        if not Decimal("0") < self.percent <= MAX_DISCOUNT:
            raise DomainError(f"cupom {self.code}: desconto deve estar entre 0 e {MAX_DISCOUNT:.0%}")


@dataclass
class Order:
    id: str
    customer_id: str
    lines: list[OrderLine]
    coupon: Coupon | None = None
    status: str = "new"
    events: list = field(default_factory=list)

    def subtotal(self) -> Money:
        return sum((line.subtotal() for line in self.lines), ZERO)

    def total(self) -> Money:
        subtotal = self.subtotal()
        return subtotal - subtotal * self.coupon.percent if self.coupon else subtotal

    def place(self) -> None:
        """A transição de estado e TODAS as regras ficam aqui, não espalhadas pelos controladores."""
        if self.status != "new":
            raise DomainError(f"pedido {self.id} já está {self.status}")
        if not self.lines:
            raise DomainError("o pedido precisa de ao menos um item")
        if any(line.qty <= 0 for line in self.lines):
            raise DomainError("quantidade deve ser positiva")
        if sum(line.qty for line in self.lines) > MAX_ITEMS:
            raise DomainError(f"no máximo {MAX_ITEMS} itens por pedido")
        if self.total() < MIN_TOTAL:
            raise DomainError(f"pedido mínimo de {MIN_TOTAL}")
        self.status = "placed"
        self.events.append(OrderPlaced(self.id, self.customer_id, self.total()))
