"""Momento de execução, expressões livres (PEP 614) e vazamento
de memória com lru_cache em métodos."""
import functools
import gc
import weakref


# 1. O decorador roda quando o def é executado, não na chamada
def announce(func):
    print(f"decorating {func.__name__}")
    return func


print("before def")


@announce
def f():
    print("running f")


print("after def")
f()

# 2. Desde o 3.9 (PEP 614), o que vem depois de @ é qualquer expressão
registry = {"identity": lambda fn: fn}


@registry["identity"]
def g():
    return "g"


print(g())


# 3. lru_cache em método guarda self vivo
class Big:
    @functools.lru_cache(maxsize=None)
    def compute(self, x):
        return x * 2


obj = Big()
obj.compute(1)
ref = weakref.ref(obj)
del obj
gc.collect()
print("instance alive after del:", ref() is not None)


# Alternativa: cache por instância, que morre junto com ela
class Better:
    def __init__(self):
        self._cache = {}

    def compute(self, x):
        if x not in self._cache:
            self._cache[x] = x * 2
        return self._cache[x]


obj = Better()
obj.compute(1)
ref = weakref.ref(obj)
del obj
gc.collect()
print("instance alive after del:", ref() is not None)
