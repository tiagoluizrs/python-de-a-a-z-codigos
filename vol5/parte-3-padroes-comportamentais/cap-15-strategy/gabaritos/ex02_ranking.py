"""Gabarito do exercício 2."""
import heapq
from types import SimpleNamespace


def by_attr(name, descending=False):
    def key(item):
        value = item[name] if isinstance(item, dict) else getattr(item, name)
        return -value if descending else value

    return SimpleNamespace(key=key, descending=descending)


def rank(items, *strategies, reverse=False):
    if not strategies:
        result = list(items)
    else:
        result = sorted(items, key=lambda item: tuple(s.key(item) for s in strategies))
    return result[::-1] if reverse else result


def top_n(items, strategy, n):
    if n < 0:
        raise ValueError("n negativo")
    return heapq.nsmallest(n, items, key=strategy.key)


def weighted(**weights):
    if not weights:
        raise ValueError("sem pesos")

    def key(item):
        return -sum(w * item[field] for field, w in weights.items())

    return SimpleNamespace(key=key, descending=True)
