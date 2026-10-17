"""Gabarito do exercício 1."""


def invert(mapping: dict) -> dict:
    result: dict = {}
    for key, value in mapping.items():
        # setdefault cria a lista na primeira vez que o valor aparece
        result.setdefault(value, []).append(key)
    return result
