"""Um vetor 2D completo: aritmética, escalar dos dois lados e sum()."""
import math


class Vec2:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec2({self.x!r}, {self.y!r})"

    # --- aritmética entre vetores
    def __add__(self, other):
        if not isinstance(other, Vec2):
            return NotImplemented              # deixa o Python tentar o outro lado
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vec2):
            return NotImplemented
        return Vec2(self.x - other.x, self.y - other.y)

    def __radd__(self, other):
        if other == 0:                          # permite sum(vetores)
            return self
        return NotImplemented

    # --- escalar: v * 3 e 3 * v
    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vec2(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__                          # 3 * v reaproveita o mesmo código

    def __truediv__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vec2(self.x / scalar, self.y / scalar)

    def __matmul__(self, other):                # v @ w = produto escalar
        if not isinstance(other, Vec2):
            return NotImplemented
        return self.x * other.x + self.y * other.y

    # --- unários
    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(self.x or self.y)

    # --- igualdade e hash (mesmos campos)
    def __eq__(self, other):
        if not isinstance(other, Vec2):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))


a, b = Vec2(1, 2), Vec2(3, 4)
print(a + b, a - b, -a, abs(b), a @ b)
print(a * 3, 3 * a, b / 2)
print(sum([a, b, Vec2(10, 10)]))
print(bool(Vec2(0, 0)), bool(a), a == Vec2(1, 2), a == (1, 2))
print({a: "chave"}[Vec2(1, 2)])

for label, action in (("a + 1", lambda: a + 1), ("a * a", lambda: a * a),
                      ("'x' + a", lambda: "x" + a),
                      ("a < b", lambda: a < b)):
    try:
        action()
    except TypeError as error:
        print(f"{label:<8}TypeError: {error}")
