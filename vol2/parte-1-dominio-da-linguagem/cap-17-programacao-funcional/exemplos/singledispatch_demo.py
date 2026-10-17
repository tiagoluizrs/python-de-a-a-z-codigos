"""singledispatch: sobrecarga por tipo do primeiro argumento."""
import timeit
from collections.abc import Mapping, Sequence
from decimal import Decimal
from functools import singledispatch, singledispatchmethod


@singledispatch
def to_text(value):
    return f"<{type(value).__name__}>"                      # versão genérica


@to_text.register
def _(value: int):                                          # o tipo vem da anotação
    return f"int:{value}"


@to_text.register(float)
def _(value):                                               # ou explícito
    return f"float:{value:.2f}"


@to_text.register
def _(value: Sequence):                                     # ABC: serve para list, tuple, ...
    return "[" + ", ".join(to_text(v) for v in value) + "]"


@to_text.register
def _(value: Mapping):
    return "{" + ", ".join(f"{k}={to_text(v)}" for k, v in value.items()) + "}"


@to_text.register(str)                                      # str é Sequence, mas a classe mais específica vence
def _(value):
    return repr(value)


@to_text.register(bool)                                     # bool é subclasse de int
def _(value):
    return "yes" if value else "no"


print(to_text(3), to_text(2.5), to_text([1, "a", (2.0, True)]), to_text({"k": 1}))
print(to_text(Decimal("1.5")), to_text(None), to_text(b"x"))
print(to_text.dispatch(bool)(True), to_text.dispatch(bytes) is to_text.registry[object])   # bytes é Sequence!
print(sorted(cls.__name__ for cls in to_text.registry))

# Só o PRIMEIRO argumento decide
@singledispatch
def combine(a, b):
    return "genérico"


@combine.register
def _(a: int, b):
    return "int + qualquer"


print(combine(1, "x"), combine("x", 1))

# Registrar o MESMO tipo duas vezes substitui o registro anterior (sem aviso)
@singledispatch
def kind(x):
    return "object"


@kind.register
def _(x: int):
    return "int"


@kind.register
def _(x: int | str):                                       # registra int E str
    return "int|str"


print(kind(1), kind("a"))                                  # int perdeu a função anterior


# singledispatchmethod: o despacho usa o primeiro argumento depois de self
class Renderer:
    @singledispatchmethod
    def render(self, value):
        return f"?{value!r}"

    @render.register
    def _(self, value: int):
        return f"#{value}"

    @render.register
    def _(self, value: list):
        return "".join(self.render(v) for v in value)


print(Renderer().render([1, 2, "a"]))

# Custo
@singledispatch
def f(x):
    return 0


@f.register(int)
def _(x):
    return 1


def g(x):
    if isinstance(x, int):
        return 1
    return 0


ns = dict(f=f, g=g)
for label, statement in [("singledispatch(int)", "f(1)"), ("singledispatch(str)", "f('a')"),
                         ("isinstance", "g(1)")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=300_000, repeat=5)) / 300_000
    print(f"  {label:<22}{seconds * 1e9:7.1f} ns")
