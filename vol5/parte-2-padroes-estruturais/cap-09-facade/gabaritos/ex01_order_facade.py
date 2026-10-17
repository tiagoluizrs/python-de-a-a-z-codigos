"""Gabarito do exercício 1."""


class OutOfStock(Exception):
    pass


class PaymentFailed(Exception):
    pass


class ShippingFailed(Exception):
    pass


class Inventory:
    def __init__(self, stock):
        self.stock, self.reserved = dict(stock), {}
        self._next = 0

    def reserve(self, sku, qty):
        if self.stock.get(sku, 0) < qty:
            raise OutOfStock(sku)
        self.stock[sku] -= qty
        self._next += 1
        token = f"res-{self._next}"
        self.reserved[token] = (sku, qty)
        return token

    def release(self, token):
        sku, qty = self.reserved.pop(token)
        self.stock[sku] += qty

    def commit(self, token):
        self.reserved.pop(token)


class Payments:
    def __init__(self):
        self.charges, self.refunds = {}, []
        self._next = 0

    def charge(self, card, cents):
        if card.startswith("0000"):
            raise PaymentFailed("cartão recusado")
        self._next += 1
        pid = f"pay-{self._next}"
        self.charges[pid] = (card, cents)
        return pid

    def refund(self, payment_id):
        self.refunds.append(self.charges.pop(payment_id))


class Shipping:
    def __init__(self, fail_for=None):
        self.fail_for = fail_for or set()
        self.scheduled = []

    def schedule(self, address, sku, qty):
        if address in self.fail_for:
            raise ShippingFailed(address)
        self.scheduled.append((address, sku, qty))
        return f"TRK-{len(self.scheduled):03d}"


class Notifications:
    def __init__(self):
        self.sent = []

    def send(self, to, text):
        self.sent.append((to, text))


PRICES = {"lapis": 150, "caderno": 1200}


class OrderFacade:
    def __init__(self, inventory, payments, shipping, notifications):
        self._inventory, self._payments, self._shipping, self._notifications = inventory, payments, shipping, notifications

    def place_order(self, sku, qty, card, address, email):
        if qty < 1:
            raise ValueError("quantidade inválida")
        price = PRICES[sku]
        token = self._inventory.reserve(sku, qty)
        try:
            payment_id = self._payments.charge(card, price * qty)
        except PaymentFailed:
            self._inventory.release(token)
            raise
        try:
            tracking = self._shipping.schedule(address, sku, qty)
        except ShippingFailed:
            self._payments.refund(payment_id)
            self._inventory.release(token)
            raise
        self._inventory.commit(token)
        self._notifications.send(email, f"pedido {payment_id} enviado: {tracking}")
        return {"payment_id": payment_id, "tracking": tracking}
