"""Exercício 1: polimorfismo e a hierarquia certa."""
import math


class Shape:
    """Base: define o contrato (``area``) e um método concreto (``describe``).

    * ``area()`` na base levanta ``NotImplementedError``;
    * ``describe()`` devolve ``"<NomeDaClasse> com área <area:.2f>"`` e usa
      ``type(self).__name__`` e ``self.area()`` (polimorfismo);
    * ``__lt__`` compara pela área (para ``sorted`` e ``max``).
    """


class Circle(Shape):
    """``Circle(radius)``: área pi * r**2."""

    def __init__(self, radius):
        raise NotImplementedError


class Rect(Shape):
    """``Rect(width, height)``: área width * height."""

    def __init__(self, width, height):
        raise NotImplementedError


class Square(Rect):
    """``Square(side)``: reaproveita ``Rect`` via ``super().__init__``.

    Guarde também ``side``. (Neste exercício a herança é imutável: não
    permita mudar largura e altura separadamente depois de criado.)
    """

    def __init__(self, side):
        raise NotImplementedError
