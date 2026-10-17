"""Gabarito do exercício 1."""
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Literal


def first[T](items: Sequence[T]) -> T | None:
    return items[0] if items else None


def apply_twice[T](func: Callable[[T], T], value: T) -> T:
    return func(func(value))


def count_words(text: str, lowercase: bool = True) -> dict[str, int]:
    words = text.lower().split() if lowercase else text.split()
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def safe_div(a: float, b: float) -> float | None:
    return None if b == 0 else a / b


def pairs[K, V](keys: Iterable[K], values: Iterable[V]) -> list[tuple[K, V]]:
    return list(zip(keys, values, strict=True))


def log_level(name: Literal["debug", "info", "warning"]) -> int:
    """``name`` só pode ser um destes textos: "debug", "info", "warning"."""
    levels: Mapping[str, int] = {"debug": 10, "info": 20, "warning": 30}
    return levels[name]
