"""Decoradores da biblioteca padrão."""
import contextlib
import dataclasses
import functools
import timeit


@functools.cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(80), fib.cache_info())


@functools.lru_cache(maxsize=2)
def square(n):
    print("computing", n)
    return n * n


for n in (1, 2, 1, 3, 2):
    square(n)
print(square.cache_info())
square.cache_clear()
print(square.cache_info())

# Argumentos precisam ser hasheáveis
try:
    square([1])
except TypeError as exc:
    print("TypeError:", exc)


# Cache em método: a chave inclui self, que fica preso no cache
class Repo:
    @functools.lru_cache(maxsize=None)
    def load(self, key):
        return key


r = Repo()
r.load("a")
print(Repo.load.cache_info().currsize)

# Vantagem do cache: tempo
def fib_plain(n):
    return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)


slow = timeit.timeit(lambda: fib_plain(25), number=3)
fast = timeit.timeit(lambda: fib(25), number=3)
print(f"cache: sem {slow*1e3:.0f} ms; com {fast*1e6:.0f} us")


@functools.total_ordering
class Version:
    def __init__(self, major, minor):
        self.major, self.minor = major, minor

    def __eq__(self, other):
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other):
        return (self.major, self.minor) < (other.major, other.minor)


print(Version(3, 14) < Version(3, 15), Version(3, 15) >= Version(3, 14))


@contextlib.contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield
    finally:
        print(f"</{name}>")


with tag("b"):
    print("text")


# contextmanager também funciona como decorador de função
@tag("section")
def render():
    print("body")


render()


@dataclasses.dataclass(frozen=True, order=True)
class Money:
    amount: int
    currency: str = "BRL"


print(Money(5), Money(5) < Money(7))


# property, staticmethod e classmethod
class Temp:
    def __init__(self, celsius):
        self._c = celsius

    @property
    def fahrenheit(self):
        return self._c * 9 / 5 + 32

    @staticmethod
    def from_f(f):
        return Temp((f - 32) * 5 / 9)

    @classmethod
    def freezing(cls):
        return cls(0)


print(Temp.freezing().fahrenheit, Temp.from_f(212)._c)
print([type(Temp.__dict__[k]).__name__
       for k in ("fahrenheit", "from_f", "freezing")])
