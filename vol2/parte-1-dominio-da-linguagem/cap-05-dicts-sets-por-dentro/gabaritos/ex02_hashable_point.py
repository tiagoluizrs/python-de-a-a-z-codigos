"""Gabarito do exercício 2."""


class Point:
    __slots__ = ("_x", "_y")

    def __init__(self, x, y):
        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)

    x = property(lambda self: self._x)    # só leitura: sem setter
    y = property(lambda self: self._y)

    def __setattr__(self, name, value):
        raise AttributeError("Point is immutable")

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented            # deixa o Python tentar o outro lado
        return (self._x, self._y) == (other._x, other._y)

    def __hash__(self):
        return hash((self._x, self._y))      # os mesmos campos do __eq__

    def __repr__(self):
        return f"Point({self._x!r}, {self._y!r})"
