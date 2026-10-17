"""Versão limpa do ``messy.py``: mesmo propósito, sem os avisos."""

from collections.abc import Iterable


def process(data: Iterable[int | None], *, double: bool = False) -> list[int]:
    """Descarta os ``None`` e, opcionalmente, dobra os valores."""
    factor = 2 if double else 1
    return [value * factor for value in data if value is not None]


def join_pair(first: object, second: object) -> str:
    """Devolve ``"first-second"``."""
    return f"{first}-{second}"


def first_argument(first: object, *_ignored: object) -> object:
    """Devolve o primeiro argumento (os demais são ignorados de propósito)."""
    return first
