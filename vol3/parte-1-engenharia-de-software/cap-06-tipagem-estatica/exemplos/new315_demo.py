"""Novidades de tipagem do 3.15: o que existe em tempo de execução."""
import typing
from typing import Any, TypedDict, TypeForm


# PEP 728: TypedDict fechado ou com itens extras de um tipo
class Closed(TypedDict, closed=True):
    a: int


class WithExtras(TypedDict, extra_items=str):
    a: int


print("closed:", Closed.__closed__, "| extra_items:", WithExtras.__extra_items__, "| padrão:", typing.TypedDict("T", {}).__closed__)


# PEP 747: TypeForm, "um valor que é um tipo"
def cast_to[T](typ: TypeForm[T], value: Any) -> T:
    return value


print("TypeForm(int) em execução devolve o próprio valor:", TypeForm(int), TypeForm(list[int]))


# PEP 800: @disjoint_base
@typing.disjoint_base
class Base:
    pass


print("disjoint_base marca a classe:", Base.__dict__.get("__disjoint_base__"))

# Removidos / obsoletos no 3.15
import warnings

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    from typing import ByteString  # noqa
print("ByteString:", [str(w.category.__name__) for w in caught])
try:
    typing.NamedTuple("P", x=int, y=int)
except TypeError as error:
    print("NamedTuple(kwargs): TypeError:", str(error)[:60])
