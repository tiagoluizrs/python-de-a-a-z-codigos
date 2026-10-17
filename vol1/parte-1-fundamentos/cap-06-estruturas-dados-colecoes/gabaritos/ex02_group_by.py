"""Gabarito do exercício 2."""
from collections.abc import Callable, Iterable


def group_by(items: Iterable, key: Callable) -> dict:
    groups: dict = {}
    for item in items:
        groups.setdefault(key(item), []).append(item)
    return groups
