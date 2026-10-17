"""Gabarito do exercício 4."""
import functools
from decimal import Decimal


class CurrencyMismatch(ValueError):
    pass


def _is_number(value):
    return isinstance(value, (int, Decimal)) and not isinstance(value, bool)


@functools.total_ordering
class Money:
    def __init__(self, amount, currency):
        self.amount = Decimal(amount)
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"

    def _same_currency(self, other):
        if self.currency != other.currency:
            raise CurrencyMismatch(f"{self.currency} != {other.currency}")

    def __add__(self, other):
        if other == 0 and not isinstance(other, Money):      # sum(): início 0
            return self
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    __radd__ = __add__

    def __sub__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor):
        if not _is_number(factor):
            return NotImplemented
        return Money(self.amount * factor, self.currency)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Money):
            self._same_currency(other)
            return self.amount / other.amount                  # razão: Decimal
        if _is_number(other):
            return Money(self.amount / other, self.currency)
        return NotImplemented

    def __neg__(self):
        return Money(-self.amount, self.currency)

    def __abs__(self):
        return Money(abs(self.amount), self.currency)

    def __bool__(self):
        return self.amount != 0

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return self.amount < other.amount

    def __hash__(self):
        return hash((self.amount, self.currency))
