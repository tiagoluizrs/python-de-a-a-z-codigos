"""Gabarito do exercício 3."""

READ, WRITE, EXECUTE = 0b001, 0b010, 0b100


def has_flag(value: int, flag: int) -> bool:
    return value & flag == flag      # & vem antes de == (diferente do C!)


def set_flag(value: int, flag: int) -> int:
    return value | flag


def clear_flag(value: int, flag: int) -> int:
    return value & ~flag


def toggle_flag(value: int, flag: int) -> int:
    return value ^ flag


def is_power_of_two(n: int) -> bool:
    # Uma potência de 2 tem um único bit ligado; n-1 liga todos os bits abaixo
    return n > 0 and n & (n - 1) == 0
