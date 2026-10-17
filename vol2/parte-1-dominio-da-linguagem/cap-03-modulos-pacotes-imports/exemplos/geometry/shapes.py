"""Formas geométricas simples."""
import math

from .utils.maths import clamp   # import relativo: mesmo pacote
from . import units               # irmão do shapes


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = clamp(radius, 0, 1_000)

    def area(self) -> float:
        return math.pi * self.radius**2


class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = clamp(width, 0, 1_000)
        self.height = clamp(height, 0, 1_000)

    def area(self) -> float:
        return self.width * self.height

    def area_in(self, unit: str) -> float:
        return self.area() * units.factor(unit)
