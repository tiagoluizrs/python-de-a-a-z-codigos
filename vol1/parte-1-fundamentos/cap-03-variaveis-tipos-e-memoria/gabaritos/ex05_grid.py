"""Gabarito do exercício 5."""


def make_grid(rows: int, cols: int, fill=0) -> list[list]:
    # A compreensão avalia [fill] * cols UMA VEZ POR LINHA: listas distintas
    return [[fill] * cols for _ in range(rows)]
