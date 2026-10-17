"""Metaclasses: a classe das classes."""
import abc
import enum


# 1) Metaclasse mínima: intercepta a CRIAÇÃO da classe
class Meta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        print(f"  Meta.__new__ criando {name}")
        namespace["created_by"] = "Meta"
        return super().__new__(mcs, name, bases, namespace)


class A(metaclass=Meta):
    pass


class B(A):                                            # herda a metaclasse
    pass


print(A.created_by, type(A).__name__, type(B).__name__)


# 2) Metaclasse que intercepta a INSTANCIAÇÃO: __call__
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self):
        print("  Config.__init__ executado")


print(Config() is Config())


# 3) Metaclasse que valida o corpo
class NoDuplicates(dict):
    def __setitem__(self, key, value):
        if key in self and not key.startswith("__"):
            raise TypeError(f"nome repetido no corpo da classe: {key}")
        super().__setitem__(key, value)


class StrictMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return NoDuplicates()


try:
    class Strict(metaclass=StrictMeta):
        def f(self):
            return 1

        def f(self):                                   # duplicado: erro
            return 2
except TypeError as error:
    print("TypeError:", error)


# 4) Conflito de metaclasses
class M1(type):
    pass


class M2(type):
    pass


class X(metaclass=M1):
    pass


class Y(metaclass=M2):
    pass


try:
    class Z(X, Y):
        pass
except TypeError as error:
    print("TypeError:", error)

# 5) Metaclasses que você já usa
print(type(abc.ABC).__name__, type(enum.Enum).__name__, type(int).__name__)
