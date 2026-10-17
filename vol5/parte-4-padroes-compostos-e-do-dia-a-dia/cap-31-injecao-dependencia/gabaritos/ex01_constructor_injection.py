"""Gabarito do exercício 1."""


class PaymentDeclined(Exception):
    pass


class CheckoutService:
    def __init__(self, orders, payments, mailer, clock):
        self.orders, self.payments, self.mailer, self.clock = orders, payments, mailer, clock

    @staticmethod
    def _validate(items):
        if not items:
            raise ValueError("carrinho vazio")
        for _, qty, unit in items:
            if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
                raise ValueError("quantidade inválida")
            if not isinstance(unit, int) or isinstance(unit, bool) or unit < 0:
                raise ValueError("valor inválido")

    def checkout(self, customer, items):
        self._validate(items)
        total = sum(qty * unit for _, qty, unit in items)
        order_id = self.orders.next_id()
        payment_id = self.payments.charge(customer, total)
        order = {"id": order_id, "customer": customer, "total": total, "payment_id": payment_id, "at": self.clock()}
        try:
            self.orders.save(dict(order))
        except Exception:
            self.payments.refund(payment_id)
            raise
        try:
            self.mailer.send(customer, f"pedido {order_id} confirmado")
            order["email_sent"] = True
        except ConnectionError:
            order["email_sent"] = False
        return order
