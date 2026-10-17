"""Exercício 2: tipagem estrutural com ``Protocol``.

Defina:

* ``SupportsArea``: protocolo com ``def area(self) -> float``;
* ``Closeable``: protocolo ``@runtime_checkable`` com ``def close(self) -> None``;
* ``total_area(shapes)``: soma as áreas de um ``Iterable[SupportsArea]``;
* ``close_all(resources)``: chama ``close()`` em cada item de um
  ``Iterable[Closeable]``; devolve a lista das mensagens (``str(erro)``) dos que
  levantaram ``Exception``, SEM interromper os demais.

``Circle`` e ``Square`` abaixo NÃO herdam do protocolo e mesmo assim devem ser
aceitos. A correção roda ``mypy --strict`` e verifica que passar um objeto sem
``area()`` a ``total_area`` é um ERRO de tipo.
"""
import math
from collections.abc import Iterable
from typing import Protocol, runtime_checkable


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius**2


class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side**2


def total_area(shapes):
    raise NotImplementedError


def close_all(resources):
    raise NotImplementedError
