"""Gabarito do exercício 3."""


def percent(p):
    if not 0 <= p <= 100:
        raise ValueError(f"percentual inválido: {p}")
    return lambda total: total * (1 - p / 100)


def fixed(amount):
    if amount < 0:
        raise ValueError("valor negativo")
    return lambda total: max(total - amount, 0.0)


def tiered(*tiers):
    if not tiers:
        raise ValueError("sem faixas")
    ordered = sorted(tiers)

    def apply(total):
        chosen = None
        for minimum, p in ordered:
            if minimum <= total:
                chosen = p
        return total if chosen is None else total * (1 - chosen / 100)

    return apply


def best_of(*strategies):
    if not strategies:
        raise ValueError("sem estratégias")
    return lambda total: min(s(total) for s in strategies)


def then(*strategies):
    def apply(total):
        for s in strategies:
            total = s(total)
        return total
    return apply


def checkout(subtotal, strategy=None):
    if subtotal < 0:
        raise ValueError("subtotal negativo")
    return round(strategy(subtotal) if strategy else subtotal, 2)
