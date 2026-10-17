"""Os sete sabores de callable e métodos ligados."""
import asyncio
import inspect


def plain(x):
    return x


class Counter:
    def __init__(self):
        self.n = 0

    def __call__(self):
        self.n += 1
        return self.n

    def method(self):
        return self.n


def gen():
    yield 1


async def coro():
    return 1


flavors = {
    "funcao": plain,
    "lambda": lambda x: x,
    "metodo ligado": Counter().method,
    "classe": Counter,
    "instancia": Counter(),
    "generator fn": gen,
    "corrotina fn": coro,
    "builtin": len,
}
for name, obj in flavors.items():
    print(f"{name:14s} callable={callable(obj)!s:5s} {type(obj).__name__}")
print(callable(42), callable("x"), callable(None))

c = Counter()
c(); c()
print(c(), c.n)

# métodos ligados vs funções
b = c.method
print(b, type(b))
print(b.__self__ is c, b.__func__ is Counter.method)
print(Counter.method, type(Counter.method))
print(Counter.method(c) == b())
# a função em si é um descritor: __get__ cria o método ligado
bound = Counter.method.__get__(c)
print(bound == b, bound is b)

# gen e coro: chamar NÃO executa o corpo
g = gen()
print(type(g).__name__, inspect.isgeneratorfunction(gen))
co = coro()
print(type(co).__name__, inspect.iscoroutinefunction(coro))
print(asyncio.run(co))


# custo de chamar cada sabor (1 argumento)
import timeit


def f(x):
    return x


class C:
    def m(self, x):
        return x

    def __call__(self, x):
        return x


c = C()
b = c.m
N = 2_000_000
for label, stmt in [("funcao f(1)", "f(1)"), ("instancia c(1)", "c(1)"),
                    ("metodo ligado b(1)", "b(1)"),
                    ("C.m(c, 1)", "C.m(c, 1)"), ("c.m(1)", "c.m(1)")]:
    t = min(timeit.repeat(stmt, globals=globals(), number=N,
                          repeat=5)) / N
    print(f"{label:20s} {t * 1e9:6.1f} ns")
