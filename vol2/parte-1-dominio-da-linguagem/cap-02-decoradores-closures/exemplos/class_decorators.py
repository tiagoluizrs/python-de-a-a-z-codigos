"""Decoradores como classes, e decoradores de classes."""
import functools


class CountCalls:
    """Decorador com estado: conta quantas vezes foi chamado."""

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


@CountCalls
def ping():
    """Responde pong."""
    return "pong"


ping()
ping()
print(ping.calls, ping.__name__, ping.__doc__, ping())


# Armadilha: instância de classe não vira método (sem __get__)
class Service:
    @CountCalls
    def run(self):
        return "ran"


try:
    Service().run()
except TypeError as exc:
    print("TypeError:", exc)


# Correção: implementar o protocolo descritor __get__
class CountCallsMethod(CountCalls):
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return functools.partial(self, obj)


class Service2:
    @CountCallsMethod
    def run(self):
        return "ran"


print(Service2().run(), Service2.run.calls)


# Decorador de CLASSE: recebe a classe, devolve a classe
def add_repr(cls):
    fields = list(cls.__init__.__code__.co_varnames[1:])

    def __repr__(self):
        body = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
        return f"{cls.__name__}({body})"

    cls.__repr__ = __repr__
    return cls


@add_repr
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


print(Point(1, 2))
