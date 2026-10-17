"""Gabarito do exercício 2."""


def chunked(items: list, size: int) -> list[list]:
    if size < 1:
        raise ValueError("size must be >= 1")
    return [items[i:i + size] for i in range(0, len(items), size)]
