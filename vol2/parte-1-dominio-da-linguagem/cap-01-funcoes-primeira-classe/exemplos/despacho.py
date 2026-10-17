"""singledispatch, singledispatchmethod e tabelas de despacho."""
import functools
from decimal import Decimal


@functools.singledispatch
def render(value):
    return f"<{type(value).__name__}> {value}"


@render.register
def _(value: int):
    return f"int:{value}"


@render.register
def _(value: list):
    return "[" + ", ".join(render(v) for v in value) + "]"


@render.register(float)
@render.register(Decimal)
def _(value):
    return f"num:{value:.2f}"


@render.register
def _(value: str | bytes):          # união de tipos (3.11+)
    return f"text:{value!r}"


print(render(3), render(2.5), render(Decimal("1.234")))
print(render(["a", 1, [2.0]]), render(None), render(True))
print(render.dispatch(bool), render.dispatch(dict))
print(sorted(t.__name__ for t in render.registry))


# singledispatchmethod
class Exporter:
    @functools.singledispatchmethod
    def export(self, data):
        raise NotImplementedError(type(data).__name__)

    @export.register
    def _(self, data: dict):
        return ";".join(f"{k}={v}" for k, v in data.items())

    @export.register
    def _(self, data: list):
        return ",".join(map(str, data))


e = Exporter()
print(e.export({"a": 1}), e.export([1, 2]))
try:
    e.export(3.0)
except NotImplementedError as exc:
    print("NotImplementedError:", exc)


# só o PRIMEIRO argumento decide
@functools.singledispatch
def add(a, b):
    return "generic"


@add.register
def _(a: int, b):
    return f"int + {type(b).__name__}"


print(add(1, "x"), add("x", 1))
