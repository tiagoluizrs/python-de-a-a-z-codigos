"""Exercício 1: uma facade sobre um subsistema com ORDEM de uso e DESFAZER (compensações)."""


class OutOfStock(Exception):
    pass


class PaymentFailed(Exception):
    pass


class ShippingFailed(Exception):
    pass


# ---- o subsistema (NÃO edite) ----
class Inventory:
    def __init__(self, stock: dict):
        self.stock, self.reserved = dict(stock), {}
        self._next = 0

    def reserve(self, sku: str, qty: int) -> str:
        if self.stock.get(sku, 0) < qty:
            raise OutOfStock(sku)
        self.stock[sku] -= qty
        self._next += 1
        token = f"res-{self._next}"
        self.reserved[token] = (sku, qty)
        return token

    def release(self, token: str) -> None:
        sku, qty = self.reserved.pop(token)
        self.stock[sku] += qty

    def commit(self, token: str) -> None:
        self.reserved.pop(token)


class Payments:
    def __init__(self):
        self.charges, self.refunds = {}, []
        self._next = 0

    def charge(self, card: str, cents: int) -> str:
        if card.startswith("0000"):
            raise PaymentFailed("cartão recusado")
        self._next += 1
        pid = f"pay-{self._next}"
        self.charges[pid] = (card, cents)
        return pid

    def refund(self, payment_id: str) -> None:
        self.refunds.append(self.charges.pop(payment_id))


class Shipping:
    def __init__(self, fail_for: set | None = None):
        self.fail_for = fail_for or set()
        self.scheduled = []

    def schedule(self, address: str, sku: str, qty: int) -> str:
        if address in self.fail_for:
            raise ShippingFailed(address)
        self.scheduled.append((address, sku, qty))
        return f"TRK-{len(self.scheduled):03d}"


class Notifications:
    def __init__(self):
        self.sent = []

    def send(self, to: str, text: str) -> None:
        self.sent.append((to, text))


PRICES = {"lapis": 150, "caderno": 1200}


class OrderFacade:
    """``OrderFacade(inventory, payments, shipping, notifications)`` e ``place_order(sku, qty, card, address, email) -> dict``.

    A ordem é: (1) ``inventory.reserve``; (2) ``payments.charge(card, PRICES[sku] * qty)``; (3) ``shipping.schedule``; (4) ``inventory.commit``;
    (5) ``notifications.send(email, f"pedido {payment_id} enviado: {tracking}")``; devolve ``{"payment_id": ..., "tracking": ...}``.

    Falhas (cada uma DESFAZ o que já foi feito e deixa o subsistema como estava, e propaga a exceção original):

    * ``qty`` menor que 1: ``ValueError("quantidade inválida")``, ANTES de tocar no subsistema; ``sku`` fora de ``PRICES``: ``KeyError`` (também antes);
    * ``OutOfStock`` na reserva: nada a desfazer;
    * ``PaymentFailed``: ``inventory.release(token)``;
    * ``ShippingFailed``: ``payments.refund(payment_id)`` E ``inventory.release(token)`` (nessa ordem);
    * nenhuma notificação é enviada em caso de falha."""

    def __init__(self, inventory, payments, shipping, notifications):
        raise NotImplementedError

    def place_order(self, sku: str, qty: int, card: str, address: str, email: str) -> dict:
        raise NotImplementedError
