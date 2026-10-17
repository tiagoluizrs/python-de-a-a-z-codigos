"""Gabarito do exercício 1."""


class InvalidTransition(Exception):
    pass


class State:
    name = "?"

    def pay(self, order):
        self._deny("pay")

    def ship(self, order):
        self._deny("ship")

    def deliver(self, order):
        self._deny("deliver")

    def cancel(self, order):
        self._deny("cancel")

    def _deny(self, event):
        raise InvalidTransition(f"{event} não permitido em {self.name}")


class New(State):
    name = "new"

    def pay(self, order):
        order.state = Paid()

    def cancel(self, order):
        order.state = Cancelled()


class Paid(State):
    name = "paid"

    def ship(self, order):
        order.state = Shipped()

    def cancel(self, order):
        order.refund = True
        order.state = Cancelled()


class Shipped(State):
    name = "shipped"

    def deliver(self, order):
        order.state = Delivered()


class Delivered(State):
    name = "delivered"


class Cancelled(State):
    name = "cancelled"


class Order:
    def __init__(self):
        self.refund = False
        self._history = []
        self._set(New())

    def _set(self, state):
        self.state = state
        self._history.append(state.name)

    def _fire(self, action):
        before = self.state
        action(self)
        if self.state is not before:
            self._history.append(self.state.name)

    def pay(self):
        self._fire(self.state.pay)

    def ship(self):
        self._fire(self.state.ship)

    def deliver(self):
        self._fire(self.state.deliver)

    def cancel(self):
        self._fire(self.state.cancel)

    @property
    def state_name(self):
        return self.state.name

    @property
    def history(self):
        return list(self._history)

    @property
    def is_final(self):
        return self.state.name in ("delivered", "cancelled")
