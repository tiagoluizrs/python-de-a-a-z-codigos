"""Funções matemáticas pequenas."""
from .. import units   # '..' sobe um nível: geometry


def clamp(value: float, low: float, high: float) -> float:
    """Limita ``value`` ao intervalo [low, high]."""
    return max(low, min(value, high))


def known_units() -> list[str]:
    return sorted(units._FACTORS)
