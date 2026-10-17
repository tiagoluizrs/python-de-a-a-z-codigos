"""O custo de sobrecarregar um operador em Python."""
import timeit
from fractions import Fraction


class Vec2:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)


class Strict:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        if not isinstance(other, Strict):
            return NotImplemented
        return Strict(self.x + other.x, self.y + other.y)


a, b = Vec2(1, 2), Vec2(3, 4)
s, t = Strict(1, 2), Strict(3, 4)
f, g = Fraction(1, 3), Fraction(1, 6)
cases = [
    ("int + int", "i + j", {"i": 1, "j": 2}),
    ("float + float", "u + v", {"u": 1.5, "v": 2.5}),
    ("tupla + tupla (2 itens)", "p + q", {"p": (1, 2), "q": (3, 4)}),
    ("Vec2 + Vec2", "a + b", {"a": a, "b": b}),
    ("Strict + Strict (com isinstance)", "s + t", {"s": s, "t": t}),
    ("Fraction + Fraction", "f + g", {"f": f, "g": g}),
]
# (com literais, `1 + 2` seria calculado pelo compilador: medir variáveis)
for label, statement, namespace in cases:
    seconds = min(timeit.repeat(statement, globals=namespace, number=500_000,
                                repeat=5)) / 500_000
    print(f"{label:<34}{seconds * 1e9:8.1f} ns")
