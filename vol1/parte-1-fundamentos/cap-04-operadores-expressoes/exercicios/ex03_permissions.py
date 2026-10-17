"""Exercício 3: permissões com operadores bit a bit."""

READ, WRITE, EXECUTE = 0b001, 0b010, 0b100


def has_flag(value: int, flag: int) -> bool:
    """True se o bit (ou bits) de ``flag`` está ligado em ``value``."""
    raise NotImplementedError


def set_flag(value: int, flag: int) -> int:
    """Devolva ``value`` com ``flag`` ligado."""
    raise NotImplementedError


def clear_flag(value: int, flag: int) -> int:
    """Devolva ``value`` com ``flag`` desligado."""
    raise NotImplementedError


def toggle_flag(value: int, flag: int) -> int:
    """Devolva ``value`` com ``flag`` invertido."""
    raise NotImplementedError


def is_power_of_two(n: int) -> bool:
    """True se ``n`` é potência de 2 (use ``n & (n - 1)``). 0 não é."""
    raise NotImplementedError
