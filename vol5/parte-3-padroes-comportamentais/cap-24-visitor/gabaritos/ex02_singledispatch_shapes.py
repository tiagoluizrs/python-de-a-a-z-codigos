"""Gabarito do exercício 2."""
import math
from dataclasses import dataclass
from functools import singledispatch


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


def _unknown(shape):
    raise TypeError(f"forma desconhecida: {type(shape).__name__}")


@singledispatch
def area(shape):
    _unknown(shape)


@area.register
def _(shape: Circle):
    return math.pi * shape.radius ** 2


@area.register
def _(shape: Rect):
    return shape.width * shape.height


@area.register
def _(shape: Triangle):
    s = (shape.a + shape.b + shape.c) / 2
    return math.sqrt(s * (s - shape.a) * (s - shape.b) * (s - shape.c))


@area.register
def _(shape: Group):
    return sum(area(item) for item in shape.shapes)


@singledispatch
def perimeter(shape):
    _unknown(shape)


@perimeter.register
def _(shape: Circle):
    return 2 * math.pi * shape.radius


@perimeter.register
def _(shape: Rect):
    return 2 * (shape.width + shape.height)


@perimeter.register
def _(shape: Triangle):
    return shape.a + shape.b + shape.c


@perimeter.register
def _(shape: Group):
    return sum(perimeter(item) for item in shape.shapes)


@singledispatch
def describe(shape):
    _unknown(shape)


@describe.register
def _(shape: Circle):
    return f"círculo de raio {shape.radius:g}"


@describe.register
def _(shape: Rect):
    if shape.width == shape.height:
        return f"quadrado de lado {shape.width:g}"
    return f"retângulo {shape.width:g}x{shape.height:g}"


@describe.register
def _(shape: Triangle):
    return f"triângulo {shape.a:g}-{shape.b:g}-{shape.c:g}"


@describe.register
def _(shape: Group):
    return f"grupo de {len(shape.shapes)} formas: " + "; ".join(describe(item) for item in shape.shapes)


@singledispatch
def count_shapes(shape):
    _unknown(shape)


@count_shapes.register(Circle)
@count_shapes.register(Rect)
@count_shapes.register(Triangle)
def _(shape):
    return 1


@count_shapes.register
def _(shape: Group):
    return sum(count_shapes(item) for item in shape.shapes)
