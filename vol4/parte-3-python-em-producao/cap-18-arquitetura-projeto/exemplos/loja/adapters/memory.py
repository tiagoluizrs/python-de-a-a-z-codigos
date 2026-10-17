"""Adaptadores em memória: rápidos, determinísticos, e ótimos para testar o núcleo sem infraestrutura."""
from loja.domain.money import Money
from loja.domain.order import Order
from loja.ports import PaymentResult


class MemoryOrderRepository:
    def __init__(self):
        self._orders: dict[str, Order] = {}

    def add(self, order: Order) -> None:
        self._orders[order.id] = order

    def get(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def list_for_customer(self, customer_id: str) -> list[Order]:
        return [o for o in self._orders.values() if o.customer_id == customer_id]


class FakeGateway:
    """Aprova tudo, a menos que o total passe do limite (para testar a recusa)."""

    def __init__(self, limit: Money = Money("10000")):
        self.limit, self.charges = limit, []

    def charge(self, order_id: str, amount: Money) -> PaymentResult:
        self.charges.append((order_id, amount))
        if amount > self.limit:
            return PaymentResult(False, reason="limite excedido")
        return PaymentResult(True, reference=f"fake-{order_id}")


class MemoryInventory:
    def __init__(self, stock: dict[str, int]):
        self.stock = dict(stock)

    def available(self, sku: str) -> int:
        return self.stock.get(sku, 0)

    def reserve(self, sku: str, qty: int) -> None:
        self.stock[sku] -= qty


class StaticPrices:
    def __init__(self, prices: dict[str, Money]):
        self.prices = prices

    def price_of(self, sku: str) -> Money:
        return self.prices[sku]


class RecordingNotifier:
    def __init__(self):
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append((to, subject, body))
