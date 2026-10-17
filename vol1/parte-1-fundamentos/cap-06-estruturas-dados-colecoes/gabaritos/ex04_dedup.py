"""Gabarito do exercício 4."""
from collections.abc import Callable, Iterable


def dedup(items: Iterable, key: Callable | None = None) -> list:
    if key is None:
        # dict.fromkeys preserva a ordem e mantém a primeira ocorrência
        return list(dict.fromkeys(items))
    seen: set = set()
    result = []
    for item in items:
        marker = key(item)
        if marker not in seen:          # busca O(1) média
            seen.add(marker)
            result.append(item)
    return result
