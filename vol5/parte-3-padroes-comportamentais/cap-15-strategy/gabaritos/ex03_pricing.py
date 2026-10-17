"""Gabarito do exercício 3."""


def no_discount(subtotal, lines):
    return 0


def _check_percent(p):
    if not 0 <= p <= 100:
        raise ValueError("percentual inválido")


def percent(p):
    _check_percent(p)
    return lambda subtotal, lines: round(subtotal * p / 100)


def bulk(min_qty, p):
    if min_qty < 1:
        raise ValueError("min_qty inválido")
    _check_percent(p)

    def strategy(subtotal, lines):
        eligible = sum(qty * unit for _, qty, unit in lines if qty >= min_qty)
        return round(eligible * p / 100)

    return strategy


class Loyalty:
    def __init__(self, threshold, p):
        if threshold < 0:
            raise ValueError("threshold inválido")
        _check_percent(p)
        self.threshold, self.p, self.orders = threshold, p, 0

    def __call__(self, subtotal, lines):
        self.orders += 1
        return round(subtotal * self.p / 100) if self.orders > self.threshold else 0

    def reset(self):
        self.orders = 0


def best_of(*strategies):
    if not strategies:
        raise ValueError("nenhuma estratégia")
    return lambda subtotal, lines: max(s(subtotal, lines) for s in strategies)


class Checkout:
    def __init__(self, strategy=None):
        self._strategy = no_discount
        self.strategy = strategy if strategy is not None else no_discount

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, value):
        if not callable(value):
            raise TypeError("estratégia precisa ser chamável")
        self._strategy = value

    def total(self, lines):
        for line in lines:
            _, qty, unit = line
            if qty <= 0 or unit < 0:
                raise ValueError(f"linha inválida: {line!r}")
        subtotal = sum(qty * unit for _, qty, unit in lines)
        discount = min(self._strategy(subtotal, lines), subtotal)
        return subtotal - discount

    def describe(self):
        return getattr(self._strategy, "__name__", type(self._strategy).__name__)
