"""@dataclass gera __init__, __repr__ e __eq__ a partir das anotações."""
import inspect
from dataclasses import dataclass


# Escrito à mão
class ManualPoint:
    def __init__(self, x, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"ManualPoint(x={self.x!r}, y={self.y!r})"

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)


# Com @dataclass: as mesmas três coisas, declaradas
@dataclass
class Point:
    x: int
    y: int = 0


p, q = Point(1, 2), Point(1, 2)
print(p, p == q, p is q)
print(Point(5))                                  # y usa o padrão
print(inspect.signature(Point))
print(Point.__eq__ is object.__eq__, Point.__hash__)   # __eq__ gerado; __hash__ = None
print(Point.__match_args__)

# As anotações NÃO são verificadas em tempo de execução
print(Point("a", [1]))

# Os campos
import dataclasses
print([(f.name, f.type, f.default) for f in dataclasses.fields(Point)])

# match/case com dataclasses (graças a __match_args__)
for point in (Point(0, 0), Point(3, 0), Point(2, 5)):
    match point:
        case Point(0, 0):
            print("origem")
        case Point(x, 0):
            print("no eixo x em", x)
        case Point(x, y):
            print("em", (x, y))
