"""Memoização: lru_cache, cache, cache_info, vazamento em métodos."""
import functools
import gc
import timeit
import weakref

calls = 0


def fib_plain(n):
    global calls
    calls += 1
    return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)


@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib_plain(25), calls)
print(fib(25), fib.cache_info())
print(fib(100))
print(fib.cache_info())
fib.cache_clear()
print(fib.cache_info())
print(fib.__wrapped__, fib.cache_parameters())

for n in (25, 30):
    t_plain = min(timeit.repeat(lambda: fib_plain(n), number=1,
                                repeat=3))
    fib.cache_clear()
    t_cold = timeit.timeit(lambda: fib(n), number=1)
    t_warm = min(timeit.repeat(lambda: fib(n), number=10_000,
                               repeat=3)) / 10_000
    print(f"n={n}: sem cache {t_plain * 1e3:.2f} ms, "
          f"cache frio {t_cold * 1e6:.1f} us, "
          f"cache quente {t_warm * 1e9:.1f} ns")


# maxsize e política LRU
@functools.lru_cache(maxsize=2)
def sq(n):
    return n * n


sq(1); sq(2); sq(1); sq(3)      # 2 sai (menos usado recentemente)
print(sq.cache_info())
sq(2)
print(sq.cache_info())

# argumentos precisam ser hasheáveis
try:
    sq([1, 2])
except TypeError as e:
    print("TypeError:", e)

# 1, 1.0 e True são a mesma chave de dict; typed=True os separa
@functools.lru_cache(maxsize=None)
def ident(x):
    return x


@functools.lru_cache(maxsize=None, typed=True)
def ident_typed(x):
    return x


for fn in (ident, ident_typed):
    print(fn(1), fn(1.0), fn(True), fn.cache_info())


# vazamento: o cache segura self
class Service:
    @functools.lru_cache(maxsize=None)
    def compute(self, n):
        return n * 2


s = Service()
s.compute(1)
ref = weakref.ref(s)
del s
gc.collect()
print("instancia ainda viva:", ref() is not None)
print(Service.compute.cache_info())


# alternativa: cache por instância, no __init__
class Service2:
    def __init__(self):
        self.compute = functools.lru_cache(maxsize=None)(self._compute)

    def _compute(self, n):
        return n * 2


s2 = Service2()
s2.compute(1)
ref2 = weakref.ref(s2)
del s2
gc.collect()
print("instancia 2 ainda viva:", ref2() is not None)


# cached_property (apenas um aperitivo)
class Report:
    def __init__(self):
        self.runs = 0

    @functools.cached_property
    def total(self):
        self.runs += 1
        return 42


r = Report()
print(r.total, r.total, r.runs, "total" in r.__dict__)
