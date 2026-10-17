"""Classes e funções de geometria plana."""
import math
from collections.abc import Iterable
from typing import Protocol


class Shape(Protocol):
    """Qualquer objeto que saiba calcular a própria área."""

    def area(self) -> float:
        """Devolve a área da forma."""
        ...


class Circle:
    """Um círculo.

    Args:
        radius: Raio do círculo, em qualquer unidade. Deve ser não negativo.

    Raises:
        ValueError: Se ``radius`` for negativo.

    Example:
        >>> Circle(2).area()
        12.566370614359172
        >>> Circle(-1)
        Traceback (most recent call last):
            ...
        ValueError: o raio não pode ser negativo: -1
    """

    def __init__(self, radius: float) -> None:
        if radius < 0:
            raise ValueError(f"o raio não pode ser negativo: {radius}")
        self.radius = radius

    def area(self) -> float:
        """Calcula a área (``pi * raio ** 2``).

        Returns:
            A área, na unidade do raio ao quadrado.
        """
        return math.pi * self.radius**2

    def __repr__(self) -> str:
        return f"Circle({self.radius!r})"


class Rectangle:
    """Um retângulo.

    Args:
        width: Largura.
        height: Altura.

    Example:
        >>> Rectangle(2, 3).area()
        6
    """

    def __init__(self, width: float, height: float) -> None:
        self.width, self.height = width, height

    def area(self) -> float:
        """Calcula a área (``largura * altura``)."""
        return self.width * self.height

    def __repr__(self) -> str:
        return f"Rectangle({self.width!r}, {self.height!r})"


def total_area(shapes: Iterable[Shape]) -> float:
    """Soma as áreas de várias formas.

    Args:
        shapes: Objetos com um método ``area()`` (veja :class:`Shape`).

    Returns:
        A soma das áreas; ``0`` se a coleção for vazia.

    Example:
        >>> total_area([Rectangle(1, 2), Rectangle(3, 4)])
        14
        >>> total_area([])
        0
    """
    return sum(shape.area() for shape in shapes)


def largest(shapes: Iterable[Shape]) -> Shape:
    """Devolve a forma de maior área.

    Args:
        shapes: Uma coleção NÃO vazia de formas.

    Returns:
        A forma com a maior área (a primeira, em caso de empate).

    Raises:
        ValueError: Se a coleção estiver vazia.

    Example:
        >>> largest([Rectangle(1, 1), Rectangle(2, 2), Rectangle(1, 3)])
        Rectangle(2, 2)
    """
    return max(shapes, key=lambda shape: shape.area())
