"""Os atributos "dunder" que todo objeto traz, e quem os define."""


class Point:
    """Um ponto."""

    def __init__(self, x, y):
        self.x, self.y = x, y


p = Point(1, 2)
print(p.__class__ is Point, type(p) is Point)
print(p.__dict__, Point.__name__, Point.__qualname__, Point.__module__)
print(Point.__doc__, Point.__mro__)
print(sorted(name for name in dir(object) if name.startswith("__"))[:12])
print(len([n for n in dir(object) if n.startswith("__")]), "métodos/atributos em object")

# object já entrega um comportamento padrão para vários protocolos
print(p == p, p == Point(1, 2), hash(p) == hash(p), bool(p))
print(type(p).__eq__ is object.__eq__, type(p).__hash__ is object.__hash__)
