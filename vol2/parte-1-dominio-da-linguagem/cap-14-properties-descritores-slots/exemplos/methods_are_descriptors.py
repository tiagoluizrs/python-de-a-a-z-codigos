"""Funções são descritores sem dados: é assim que self aparece."""


class Dog:
    def speak(self):
        return "au"

    @classmethod
    def create(cls):
        return cls()

    @staticmethod
    def helper():
        return "sem self"


print(type(Dog.__dict__["speak"]).__name__)          # function
print(type(Dog.__dict__["create"]).__name__)         # classmethod
print(type(Dog.__dict__["helper"]).__name__)         # staticmethod

dog = Dog()
speak = Dog.__dict__["speak"]
bound = speak.__get__(dog, Dog)                      # o que o ponto faz por baixo
print(bound, bound(), bound == dog.speak)
print(hasattr(speak, "__get__"), hasattr(speak, "__set__"))   # sem dados: só __get__


# Reimplementando classmethod e staticmethod em Python puro
import types


class my_classmethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        return types.MethodType(self.func, objtype)  # liga ao CLASSE, não à instância


class my_staticmethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        return self.func                              # devolve a função "crua"


class Tool:
    @my_classmethod
    def build(cls, n):
        return f"{cls.__name__}({n})"

    @my_staticmethod
    def add(a, b):
        return a + b


print(Tool.build(1), Tool().build(2), Tool.add(2, 3), Tool().add(4, 5))
