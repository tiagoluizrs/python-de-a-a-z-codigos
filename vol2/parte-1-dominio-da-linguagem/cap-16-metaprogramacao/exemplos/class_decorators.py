"""Decoradores de classe: recebem a classe pronta e devolvem uma classe."""
import functools

REGISTRY = {}


def register(cls):
    REGISTRY[cls.__name__] = cls
    return cls                                         # devolve a MESMA classe


@register
class Alpha:
    pass


@register
class Beta:
    pass


print(sorted(REGISTRY))


# Decorador com parâmetros: gera __repr__ a partir de atributos
def auto_repr(*names):
    def decorate(cls):
        def __repr__(self):
            body = ", ".join(f"{n}={getattr(self, n)!r}" for n in names)
            return f"{type(self).__name__}({body})"
        cls.__repr__ = __repr__
        return cls
    return decorate


@auto_repr("x", "y")
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


print(Point(1, 2))


# Decorador que ENVOLVE todos os métodos públicos (cuidado: custo e complexidade)
def log_calls(cls):
    for name, member in list(vars(cls).items()):
        if callable(member) and not name.startswith("_"):
            setattr(cls, name, _wrap(name, member))
    return cls


def _wrap(name, func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  -> {name}{args[1:]}")
        return func(*args, **kwargs)
    return wrapper


@log_calls
class Calc:
    def add(self, a, b):
        return a + b

    def _private(self):
        return 0


print(Calc().add(2, 3), Calc().add.__name__)


# Um decorador que SUBSTITUI a classe: cuidado com isinstance e herança
def make_final(cls):
    def __init_subclass__(cls_, **kw):
        raise TypeError(f"{cls.__name__} é final")
    cls.__init_subclass__ = classmethod(__init_subclass__)
    return cls


@make_final
class Leaf:
    pass


try:
    class Child(Leaf):
        pass
except TypeError as error:
    print("TypeError:", error)
