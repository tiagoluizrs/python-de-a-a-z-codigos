"""Exercício 3: o exemplo clássico do GoF: FORMAS (abstração) desenhadas por RENDERIZADORES (implementação)."""


def num(value: float) -> str:
    """Formata sem zeros inúteis: ``num(3)`` -> ``"3"``, ``num(2.5)`` -> ``"2.5"``, ``num(2.0)`` -> ``"2"`` (use ``f"{value:g}"``)."""
    raise NotImplementedError


class SvgRenderer:
    """``circle(x, y, r)`` -> ``'<circle cx="X" cy="Y" r="R"/>'``; ``rect(x, y, w, h)`` -> ``'<rect x="X" y="Y" width="W" height="H"/>'`` (números com ``num``)."""

    def circle(self, x, y, r) -> str:
        raise NotImplementedError

    def rect(self, x, y, w, h) -> str:
        raise NotImplementedError


class TextRenderer:
    """``circle(x, y, r)`` -> ``"circle at (X, Y) radius R"``; ``rect(x, y, w, h)`` -> ``"rect at (X, Y) size WxH"`` (números com ``num``)."""

    def circle(self, x, y, r) -> str:
        raise NotImplementedError

    def rect(self, x, y, w, h) -> str:
        raise NotImplementedError


class Shape:
    """A ABSTRAÇÃO base: guarda o ``renderer`` (a ponte). ``with_renderer(r)`` devolve uma CÓPIA RASA com outro renderizador; ``draw()`` e ``area()`` e
    ``scale(factor)`` são dos filhos. ``factor <= 0`` em ``scale``: ``ValueError("fator inválido")``."""

    def __init__(self, renderer):
        raise NotImplementedError

    def with_renderer(self, renderer) -> "Shape":
        raise NotImplementedError

    def draw(self) -> str:
        raise NotImplementedError

    def area(self) -> float:
        raise NotImplementedError

    def scale(self, factor: float) -> "Shape":
        raise NotImplementedError


class Circle(Shape):
    """``Circle(renderer, x, y, r)`` (``r > 0``, senão ``ValueError("raio inválido")``). ``draw()`` chama ``renderer.circle(x, y, r)``; ``area()`` é
    ``3.141592653589793 * r ** 2``; ``scale(f)`` devolve um círculo NOVO com ``r * f`` (mesmo centro e mesmo renderizador)."""

    def __init__(self, renderer, x, y, r):
        raise NotImplementedError


class Rectangle(Shape):
    """``Rectangle(renderer, x, y, w, h)`` (``w`` e ``h`` ``> 0``, senão ``ValueError("tamanho inválido")``). ``draw()`` chama ``renderer.rect(x, y, w, h)``;
    ``area()`` é ``w * h``; ``scale(f)`` devolve um retângulo NOVO com ``w * f`` e ``h * f`` (mesma posição e renderizador)."""

    def __init__(self, renderer, x, y, w, h):
        raise NotImplementedError


class Group(Shape):
    """``Group(renderer, shapes)``: as formas desenham com o PRÓPRIO renderizador de cada uma; ``draw()`` junta os desenhos com ``"\\n"``; ``area()`` soma as áreas;
    ``scale(f)`` devolve um grupo novo com as formas escaladas; ``with_renderer(r)`` troca o renderizador de TODAS as formas (devolve um grupo novo com
    cópias das formas). Um ``Group`` vazio desenha ``""``."""

    def __init__(self, renderer, shapes):
        raise NotImplementedError
