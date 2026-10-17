"""Herdar de dict/list: os métodos nativos NÃO chamam os seus."""
from collections import UserDict


class LowerDict(dict):
    """Pretende guardar todas as chaves em minúsculas."""

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)


d = LowerDict()
d["NAME"] = 1                               # passa pelo __setitem__: ok
print("setitem:", dict(d))
d.update({"AGE": 2})                         # update de dict NÃO chama __setitem__
print("update :", dict(d))
d.setdefault("CITY", 3)                      # setdefault também não
print("setdefault:", dict(d))
print("construtor:", dict(LowerDict(HOST=1)))     # o __init__ também ignora


class LowerUserDict(UserDict):
    """Com UserDict, todos os métodos passam pelo __setitem__."""

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)


u = LowerUserDict(HOST=1)
u["NAME"] = 1
u.update({"AGE": 2})
u.setdefault("CITY", 3)
print("UserDict:", dict(u))


# list/dict: operadores devolvem o tipo BASE, não a subclasse
class MyList(list):
    pass


ml = MyList([1, 2, 3])
print(type(ml + [4]).__name__, type(ml[:2]).__name__, type(ml.copy()).__name__)
print(type(MyList([1]) * 2).__name__)
