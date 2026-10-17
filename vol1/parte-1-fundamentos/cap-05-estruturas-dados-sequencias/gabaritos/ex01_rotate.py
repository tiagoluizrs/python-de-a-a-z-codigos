"""Gabarito do exercício 1."""


def rotate(items: list, k: int) -> list:
    if not items:
        return []
    k %= len(items)                 # % do Python devolve sempre 0 <= k < len
    return items[-k:] + items[:-k] if k else items[:]
