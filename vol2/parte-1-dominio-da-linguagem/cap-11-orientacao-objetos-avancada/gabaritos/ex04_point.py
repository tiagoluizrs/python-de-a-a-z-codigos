"""Gabarito do exercício 4."""
from numbers import Real
from operator import itemgetter


class Point(tuple):
    __slots__ = ()                              # sem __dict__

    def __new__(cls, x, y):
        for value in (x, y):
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(f"coordenada inválida: {value!r}")
        return super().__new__(cls, (x, y))     # o valor é fixado aqui

    x = property(itemgetter(0))
    y = property(itemgetter(1))

    def moved(self, dx, dy):
        return Point(self.x + dx, self.y + dy)

    def __repr__(self):
        return f"Point(x={self.x!r}, y={self.y!r})"
