"""Usar as anotações em tempo de execução: o que o Pydantic e o dataclass fazem."""
import typing
from dataclasses import dataclass, fields
from typing import Annotated, Literal, get_args, get_origin, get_type_hints


def conforms(value: object, hint: object) -> bool:
    """Um verificador de tipos em tempo de execução, minúsculo."""
    origin, args = get_origin(hint), get_args(hint)
    if hint is typing.Any:
        return True
    if hint is None or hint is type(None):
        return value is None
    if origin is None:
        if hint is float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if hint is int:
            return isinstance(value, int) and not isinstance(value, bool)
        return isinstance(value, hint)                      # type: ignore[arg-type]
    if origin is typing.Union or str(origin) == "<class 'types.UnionType'>":
        return any(conforms(value, arg) for arg in args)
    if origin is Literal:
        return value in args
    if origin is list:
        return isinstance(value, list) and all(conforms(v, args[0]) for v in value)
    if origin is dict:
        return isinstance(value, dict) and all(conforms(k, args[0]) and conforms(v, args[1]) for k, v in value.items())
    return isinstance(value, origin)


for value, hint in [(1, int), (True, int), (1, float), ("a", int | str), (None, int | None), ([1, 2], list[int]),
                    ([1, "x"], list[int]), ({"a": 1}, dict[str, int]), ("r", Literal["r", "w"]), ("x", Literal["r", "w"])]:
    print(f"conforms({value!r}, {hint}) = {conforms(value, hint)}")

print(get_origin(list[int]), get_args(list[int]), get_origin(int | None), get_args(int | None))


# dataclass guarda os tipos nos campos (mas NÃO os verifica)
@dataclass
class Item:
    name: str
    qty: int


print([(f.name, f.type) for f in fields(Item)], "| Item('x', 'muitos'):", Item("x", "muitos"))


# Annotated: metadados anexados ao tipo (usados por validadores)
class Positive: ...


def make(price: Annotated[float, Positive(), "em reais"]) -> None: ...


hints = get_type_hints(make, include_extras=True)
print(hints["price"], "|", get_args(hints["price"])[1:])
print(get_type_hints(make))                                   # sem include_extras: só float


# Validar uma chamada pelas anotações
import inspect


def checked(func):
    hints = get_type_hints(func)
    sig = inspect.signature(func)

    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for name, value in bound.arguments.items():
            if name in hints and not conforms(value, hints[name]):
                raise TypeError(f"{func.__name__}: {name}={value!r} não é {hints[name]}")
        return func(*args, **kwargs)

    return wrapper


@checked
def repeat(text: str, times: int) -> str:
    return text * times


print(repeat("ab", 2))
try:
    repeat("ab", "2")
except TypeError as error:
    print("TypeError:", error)
