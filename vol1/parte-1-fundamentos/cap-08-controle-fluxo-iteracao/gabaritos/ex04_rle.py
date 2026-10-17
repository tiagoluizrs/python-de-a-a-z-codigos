"""Gabarito do exercício 4."""
from itertools import groupby


def rle_encode(text: str) -> list[tuple[str, int]]:
    # o grupo é um iterador: contamos consumindo-o na hora
    return [(char, sum(1 for _ in group)) for char, group in groupby(text)]


def rle_decode(pairs: list[tuple[str, int]]) -> str:
    return "".join(char * count for char, count in pairs)
