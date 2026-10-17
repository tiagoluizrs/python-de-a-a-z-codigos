"""lru_cache e cache: memoização, política de despejo e armadilhas."""
import gc
import timeit
import weakref
from functools import cache, lru_cache


@lru_cache(maxsize=2)
def double(x):
    return x * 2


for value in (1, 2, 1, 3, 1):
    double(value)
print(double.cache_info(), double.cache_parameters())      # 1 foi despejado quando o 3 entrou?

# Argumentos precisam ser hasheáveis
try:
    double([1])
except TypeError as error:
    print("TypeError:", error)


# A chave distingue a FORMA da chamada
@lru_cache
def pair(a, b):
    return a + b


pair(1, 2)
pair(a=1, b=2)
pair(b=2, a=1)
print("formas distintas ->", pair.cache_info().currsize, "entradas")


# typed=True separa 1 de 1.0
@lru_cache(typed=True)
def ident(x):
    return x


ident(1)
ident(1.0)
print("typed:", ident.cache_info().currsize, "entradas")

# O cache devolve SEMPRE o mesmo objeto: cuidado com resultados mutáveis
@cache
def make_list():
    return [1, 2]


make_list().append(99)
print(make_list())


# lru_cache em método: o cache guarda self e impede a coleta
class Service:
    @lru_cache
    def compute(self, x):
        return x * 2


service = Service()
service.compute(1)
ref = weakref.ref(service)
del service
gc.collect()
print("instância ainda viva depois do del:", ref() is not None)


# Alternativa: um cache POR instância
class BetterService:
    def __init__(self):
        self.compute = lru_cache(maxsize=128)(self._compute)   # cache preso à instância

    def _compute(self, x):
        return x * 2


better = BetterService()
better.compute(1)
ref = weakref.ref(better)
del better
gc.collect()
print("com cache por instância:", ref() is not None)       # ciclo coletado pelo GC


# Memoização transforma o Fibonacci exponencial em linear
def fib_plain(n):
    return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)


@cache
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


plain = timeit.timeit(lambda: fib_plain(25), number=3) / 3
first = timeit.timeit(lambda: fib_cached(25), number=1)
hit = timeit.timeit(lambda: fib_cached(25), number=200_000) / 200_000
print(f"fib(25): sem cache {plain * 1e3:.1f} ms | 1a chamada com cache {first * 1e6:.0f} us | acerto {hit * 1e9:.0f} ns")
print(fib_cached.cache_info())


# Custo do acerto em um cache, comparado ao cálculo trivial
@lru_cache
def square(x):
    return x * x


square(3)
cached = timeit.timeit(lambda: square(3), number=1_000_000)
direct = timeit.timeit(lambda: 3 * 3, number=1_000_000)
print(f"acerto de lru_cache {cached * 1e3:.0f} ns | conta direta (via lambda) {direct * 1e3:.0f} ns")
