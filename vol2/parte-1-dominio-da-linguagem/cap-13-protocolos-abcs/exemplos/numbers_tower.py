"""A torre numérica: numbers.Number, Complex, Real, Rational, Integral."""
import numbers
from decimal import Decimal
from fractions import Fraction

samples = [True, 3, Fraction(1, 3), 2.5, 1 + 2j, Decimal("1.1")]
tower = [numbers.Integral, numbers.Rational, numbers.Real, numbers.Complex, numbers.Number]
print(f"{'valor':<18}" + "".join(f"{c.__name__:<10}" for c in tower))
for value in samples:
    print(f"{value!r:<18}" + "".join(f"{isinstance(value, c)!s:<10}" for c in tower))

# Armadilha: Decimal é Number, mas NÃO é Real
try:
    Decimal("1.1") + 1.5
except TypeError as error:
    print("TypeError:", error)


def double(value):
    if not isinstance(value, numbers.Number):
        raise TypeError("não é número")
    return value * 2


print(double(3), double(Fraction(1, 3)), double(Decimal("1.5")))
