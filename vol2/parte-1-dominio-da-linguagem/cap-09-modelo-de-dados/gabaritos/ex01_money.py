"""Gabarito do exercício 1."""


class Money:
    def __init__(self, cents, currency="BRL"):
        self.cents = cents
        self.currency = currency

    def __repr__(self):
        return f"Money({self.cents!r}, {self.currency!r})"

    def __str__(self):
        units, cents = divmod(self.cents, 100)
        if self.currency == "BRL":
            return f"R$ {units},{cents:02d}"
        return f"{self.currency} {units}.{cents:02d}"

    def __format__(self, spec):
        if spec == "":
            return str(self)
        if spec == "plain":
            return f"{self.cents / 100:.2f}"
        if spec == "code":
            return f"{self.currency} {self.cents / 100:.2f}"
        raise ValueError(f"formato desconhecido: {spec!r}")

    def __bool__(self):
        return self.cents != 0

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.cents, self.currency) == (other.cents, other.currency)

    def __hash__(self):
        return hash((self.cents, self.currency))     # mesmos campos do __eq__
