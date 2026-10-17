"""Gabarito do exercício 4."""


def flatten(nested: list[list]) -> list:
    return [item for inner in nested for item in inner]


def transpose(matrix: list[list]) -> list[list]:
    return [list(column) for column in zip(*matrix)]
