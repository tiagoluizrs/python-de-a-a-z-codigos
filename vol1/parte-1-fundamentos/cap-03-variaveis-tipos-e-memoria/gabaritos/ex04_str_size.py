"""Gabarito do exercício 4."""


def predicted_str_size(text: str) -> int:
    n = len(text)
    highest = max(map(ord, text), default=0)
    if highest < 128:
        return 40 + n + 1
    if highest < 256:
        return 56 + n + 1
    if highest < 65536:
        return 56 + 2 * n + 2
    return 56 + 4 * n + 4
