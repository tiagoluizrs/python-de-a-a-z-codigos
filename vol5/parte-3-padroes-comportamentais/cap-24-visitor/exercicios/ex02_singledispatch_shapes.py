"""Exercício 2: ``functools.singledispatch``: operações sobre formas que NÃO têm métodos (as classes são "de outra biblioteca")."""
import math
from dataclasses import dataclass
from functools import singledispatch


# ---- (Pronto, NÃO edite.) As formas: dados puros, com validação ----
@dataclass(frozen=True)
class Circle:
    radius: float

    def __post_init__(self):
        if self.radius <= 0:
            raise ValueError("medida inválida")


@dataclass(frozen=True)
class Rect:
    width: float
    height: float

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("medida inválida")


@dataclass(frozen=True)
class Triangle:
    a: float
    b: float
    c: float

    def __post_init__(self):
        a, b, c = sorted((self.a, self.b, self.c))
        if a <= 0 or a + b <= c:
            raise ValueError("triângulo inválido")


@dataclass(frozen=True)
class Group:
    shapes: tuple

    def __post_init__(self):
        object.__setattr__(self, "shapes", tuple(self.shapes))


# ---- Implemente as quatro funções com ``@singledispatch`` + ``register`` (uma por tipo). O tipo fora do registro: ``TypeError(f"forma desconhecida: {nome do tipo}")`` ----
def area(shape) -> float:
    """``Circle``: ``pi * r**2``; ``Rect``: ``w * h``; ``Triangle``: fórmula de Heron (``s = (a+b+c)/2``, ``sqrt(s(s-a)(s-b)(s-c))``); ``Group``: a SOMA das áreas dos membros (vazio: ``0``)."""
    raise NotImplementedError


def perimeter(shape) -> float:
    """``Circle``: ``2 * pi * r``; ``Rect``: ``2 * (w + h)``; ``Triangle``: ``a + b + c``; ``Group``: a soma dos perímetros dos membros."""
    raise NotImplementedError


def describe(shape) -> str:
    """``Circle``: ``"círculo de raio 2"``; ``Rect``: ``"retângulo 3x4"`` (e, se ``w == h``, ``"quadrado de lado 3"``); ``Triangle``: ``"triângulo 3-4-5"``; ``Group``:
    ``"grupo de N formas: d1; d2; ..."`` (``N`` é o número de membros DIRETOS e as descrições vêm de ``describe`` de cada um). Os números usam ``format(x, "g")`` (``2.0`` vira ``2``)."""
    raise NotImplementedError


def count_shapes(shape) -> int:
    """Quantas formas SIMPLES existem: ``Circle``/``Rect``/``Triangle`` valem ``1``; ``Group`` soma as dos membros (recursivamente; um grupo vazio vale ``0``)."""
    raise NotImplementedError
