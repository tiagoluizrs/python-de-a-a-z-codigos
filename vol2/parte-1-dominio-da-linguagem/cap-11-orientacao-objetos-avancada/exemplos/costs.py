"""Custo de criar objetos e de acessar atributos."""
import sys
import timeit
from collections import namedtuple
from dataclasses import dataclass


class Plain:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c


class Slotted:
    __slots__ = ("a", "b", "c")

    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c


@dataclass
class Data:
    a: int
    b: int
    c: int


Named = namedtuple("Named", "a b c")


class WithNew:
    def __new__(cls, a, b, c):
        self = super().__new__(cls)
        self.a, self.b, self.c = a, b, c
        return self


creation = [
    ("classe comum", "Plain(1, 2, 3)"),
    ("com __slots__", "Slotted(1, 2, 3)"),
    ("dataclass", "Data(1, 2, 3)"),
    ("namedtuple", "Named(1, 2, 3)"),
    ("tupla (variáveis)", "(x, y, z)"),
    ("dict", "{'a': 1, 'b': 2, 'c': 3}"),
    ("classe com __new__ próprio", "WithNew(1, 2, 3)"),
]
ns = {"Plain": Plain, "Slotted": Slotted, "Data": Data, "Named": Named,
      "WithNew": WithNew, "x": 1, "y": 2, "z": 3}
print("criação:")
for label, statement in creation:
    seconds = min(timeit.repeat(statement, globals=ns, number=300_000,
                                repeat=5)) / 300_000
    print(f"  {label:<28}{seconds * 1e9:7.1f} ns")

obj, slotted = Plain(1, 2, 3), Slotted(1, 2, 3)
class_attr = type("K", (), {"v": 1})()
ns2 = {"obj": obj, "slotted": slotted, "k": class_attr}
print("leitura de atributo:")
for label, statement in (("instância", "obj.a"), ("__slots__", "slotted.a"),
                         ("da classe (via instância)", "k.v")):
    seconds = min(timeit.repeat(statement, globals=ns2, number=1_000_000,
                                repeat=5)) / 1_000_000
    print(f"  {label:<28}{seconds * 1e9:7.1f} ns")
print("tamanho:", sys.getsizeof(obj), sys.getsizeof(slotted))
