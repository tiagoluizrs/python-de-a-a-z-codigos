"""Custo de property, descritor e slots."""
import timeit


class Plain:
    def __init__(self):
        self.x = 1
        self._y = 1

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value


class PositiveDescriptor:
    def __set_name__(self, owner, name):
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        setattr(obj, self.private, value)


class WithDescriptor:
    z = PositiveDescriptor()

    def __init__(self):
        self.z = 1


class Slotted:
    __slots__ = ("x",)

    def __init__(self):
        self.x = 1


plain, desc, slotted = Plain(), WithDescriptor(), Slotted()
ns = {"plain": plain, "desc": desc, "slotted": slotted}
rows = [
    ("ler atributo comum", "plain.x"),
    ("ler property", "plain.y"),
    ("ler descritor próprio", "desc.z"),
    ("ler atributo com __slots__", "slotted.x"),
    ("gravar atributo comum", "plain.x = 2"),
    ("gravar property (setter)", "plain.y = 2"),
    ("gravar descritor próprio", "desc.z = 2"),
    ("gravar atributo com __slots__", "slotted.x = 2"),
]
for label, statement in rows:
    seconds = min(timeit.repeat(statement, globals=ns, number=1_000_000,
                                repeat=5)) / 1_000_000
    print(f"{label:<32}{seconds * 1e9:7.1f} ns")
