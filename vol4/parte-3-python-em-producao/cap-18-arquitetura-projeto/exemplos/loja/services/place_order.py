"""O caso de uso: orquestra o domínio e as portas. Não sabe se o banco é SQLite ou Postgres, nem se o pagamento é HTTP."""
import uuid
from dataclasses import dataclass
from decimal import Decimal

from loja.domain.order import Coupon, DomainError, Order, OrderLine
from loja.ports import Inventory, Notifier, OrderRepository, PaymentGateway, PriceList


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: str
    items: tuple[tuple[str, int], ...]            # (sku, quantidade)
    coupon_code: str | None = None
    coupon_percent: Decimal | None = None


class PaymentDeclined(DomainError):
    pass


class PlaceOrder:
    def __init__(self, repo: OrderRepository, gateway: PaymentGateway, inventory: Inventory, prices: PriceList, notifier: Notifier):
        self.repo, self.gateway, self.inventory, self.prices, self.notifier = repo, gateway, inventory, prices, notifier

    def __call__(self, cmd: PlaceOrderCommand) -> Order:
        lines = [OrderLine(sku, qty, self.prices.price_of(sku)) for sku, qty in cmd.items]
        coupon = Coupon(cmd.coupon_code, cmd.coupon_percent) if cmd.coupon_code else None
        order = Order(id=uuid.uuid4().hex[:8], customer_id=cmd.customer_id, lines=lines, coupon=coupon)
        for line in order.lines:                                               # regra que depende do mundo de fora: estoque
            if self.inventory.available(line.sku) < line.qty:
                raise DomainError(f"sem estoque de {line.sku}")
        order.place()                                                          # regras puras do domínio
        result = self.gateway.charge(order.id, order.total())                  # efeito colateral nº 1
        if not result.approved:
            raise PaymentDeclined(f"pagamento recusado: {result.reason}")
        for line in order.lines:
            self.inventory.reserve(line.sku, line.qty)
        self.repo.add(order)                                                   # efeito colateral nº 2
        for event in order.events:                                             # efeito colateral nº 3, DEPOIS de persistir
            self.notifier.send(cmd.customer_id, "Pedido confirmado", f"{event.order_id}: {event.total}")
        order.events.clear()
        return order
