"""Encapsulamento por convenção: _x e __x (name mangling)."""


class Account:
    bank = "Python Bank"

    def __init__(self, owner, balance):
        self.owner = owner              # público
        self._balance = balance         # "interno" por convenção
        self.__pin = "1234"             # name mangling

    def check_pin(self, pin):
        return pin == self.__pin


acct = Account("Ana", 100)
print(vars(acct))
print(acct._balance)                    # funciona: é só um aviso
try:
    acct.__pin
except AttributeError as error:
    print("AttributeError:", error)
print(acct._Account__pin)               # o nome real é _Account__pin


# Para quê serve o mangling: evitar colisão entre classes da herança
class Parent:
    def __init__(self):
        self.__secret = "parent"

    def parent_secret(self):
        return self.__secret


class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__secret = "child"          # outro nome: _Child__secret

    def child_secret(self):
        return self.__secret


child = Child()
print(child.parent_secret(), child.child_secret(), sorted(vars(child)))


# Módulos: o underscore também vale; `import *` respeita
import json

print([name for name in dir(json) if name.startswith("_") and not name.startswith("__")][:4])
