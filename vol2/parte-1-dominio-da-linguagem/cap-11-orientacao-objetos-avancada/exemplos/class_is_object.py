"""Classes são objetos: o `class` é uma instrução executada em tempo de execução."""


class Point:
    """Um ponto."""
    dimensions = 2

    def __init__(self, x, y):
        self.x, self.y = x, y

    def norm(self):
        return (self.x**2 + self.y**2) ** 0.5


print(type(Point), type(Point(1, 2)), type(type))
print(isinstance(Point, type), Point.__name__, Point.dimensions)

# A mesma classe, criada "à mão" com type(nome, bases, namespace)
def init(self, x, y):
    self.x, self.y = x, y


Dynamic = type("Dynamic", (), {"dimensions": 2, "__init__": init,
                                "norm": lambda self: (self.x**2 + self.y**2) ** 0.5})
print(Dynamic(3, 4).norm(), Dynamic.__name__)

# Classes podem ser guardadas, passadas e devolvidas
factories = {"p": Point, "d": Dynamic}
print([factories[key](3, 4).norm() for key in factories])


def make_class(base_dimensions):
    class Local:
        dimensions = base_dimensions
    return Local


print(make_class(5).dimensions, make_class(7) is make_class(7))
print(Point.__dict__.keys() >= {"dimensions", "__init__", "norm"})
