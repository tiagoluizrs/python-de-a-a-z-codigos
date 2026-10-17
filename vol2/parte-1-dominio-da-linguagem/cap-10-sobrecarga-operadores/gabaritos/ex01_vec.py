"""Gabarito do exercício 1."""
import math


class Vec:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        object.__setattr__(self, "x", x)               # imutável
        object.__setattr__(self, "y", y)

    def __setattr__(self, name, value):
        raise AttributeError("Vec é imutável")

    def __repr__(self):
        return f"Vec({self.x!r}, {self.y!r})"

    def __add__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        if other == 0:                                  # o início de sum()
            return self
        return NotImplemented

    def __sub__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        if isinstance(scalar, bool) or not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vec(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__                                  # 2 * v

    def __truediv__(self, scalar):
        if isinstance(scalar, bool) or not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vec(self.x / scalar, self.y / scalar)

    def __matmul__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return self.x * other.x + self.y * other.y

    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(self.x or self.y)

    def __eq__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))
