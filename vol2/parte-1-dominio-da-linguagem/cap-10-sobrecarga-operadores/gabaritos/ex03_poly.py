"""Gabarito do exercício 3."""


class Poly:
    def __init__(self, coefficients):
        coefficients = list(coefficients)
        while coefficients and coefficients[-1] == 0:      # normaliza
            coefficients.pop()
        self.coefficients = tuple(coefficients)

    @property
    def degree(self):
        return len(self.coefficients) - 1

    def __repr__(self):
        return f"Poly({list(self.coefficients)!r})"

    @staticmethod
    def _lift(value):
        if isinstance(value, Poly):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            return Poly([value])
        return None

    def __add__(self, other):
        other = self._lift(other)
        if other is None:
            return NotImplemented
        size = max(len(self.coefficients), len(other.coefficients))
        a = self.coefficients + (0,) * (size - len(self.coefficients))
        b = other.coefficients + (0,) * (size - len(other.coefficients))
        return Poly(x + y for x, y in zip(a, b))

    __radd__ = __add__

    def __neg__(self):
        return Poly(-c for c in self.coefficients)

    def __sub__(self, other):
        other = self._lift(other)
        if other is None:
            return NotImplemented
        return self + (-other)

    def __rsub__(self, other):
        other = self._lift(other)
        if other is None:
            return NotImplemented
        return other + (-self)

    def __mul__(self, other):
        other = self._lift(other)
        if other is None:
            return NotImplemented
        if not self.coefficients or not other.coefficients:
            return Poly([])
        result = [0] * (len(self.coefficients) + len(other.coefficients) - 1)
        for i, a in enumerate(self.coefficients):
            for j, b in enumerate(other.coefficients):
                result[i + j] += a * b
        return Poly(result)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 0:
            return NotImplemented
        result = Poly([1])
        for _ in range(exponent):
            result = result * self
        return result

    def __call__(self, x):
        total = 0
        for coefficient in reversed(self.coefficients):    # Horner
            total = total * x + coefficient
        return total

    def __eq__(self, other):
        other = self._lift(other)
        if other is None:
            return NotImplemented
        return self.coefficients == other.coefficients

    def __hash__(self):
        return hash(self.coefficients)

    def __bool__(self):
        return bool(self.coefficients)
