"""As PORTAS: o que o núcleo precisa do mundo de fora, descrito como interfaces (Protocol).

O núcleo (domínio e serviços) depende destas interfaces; os adaptadores as implementam. Nunca o contrário.
"""
from dataclasses import dataclass
from typing import Protocol

from loja.domain.money import Money
from loja.domain.order import Order


@dataclass(frozen=True)
class PaymentResult:
    approved: bool
    reference: str = ""
    reason: str = ""


class OrderRepository(Protocol):
    def add(self, order: Order) -> None: ...
    def get(self, order_id: str) -> Order | None: ...
    def list_for_customer(self, customer_id: str) -> list[Order]: ...


class PaymentGateway(Protocol):
    def charge(self, order_id: str, amount: Money) -> PaymentResult: ...


class Inventory(Protocol):
    def available(self, sku: str) -> int: ...
    def reserve(self, sku: str, qty: int) -> None: ...


class PriceList(Protocol):
    def price_of(self, sku: str) -> Money: ...


class Notifier(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...
