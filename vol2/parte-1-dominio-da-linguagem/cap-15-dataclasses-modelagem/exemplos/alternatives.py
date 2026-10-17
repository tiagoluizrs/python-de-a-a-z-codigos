"""dataclass, NamedTuple, namedtuple, dict, TypedDict: custo e memória."""
import sys
import timeit
import tracemalloc
from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple, TypedDict


@dataclass
class DC:
    a: int
    b: int
    c: int


@dataclass(slots=True)
class DCSlots:
    a: int
    b: int
    c: int


@dataclass(frozen=True)
class DCFrozen:
    a: int
    b: int
    c: int


@dataclass(frozen=True, slots=True)
class DCFrozenSlots:
    a: int
    b: int
    c: int


class NT(NamedTuple):
    a: int
    b: int
    c: int


NamedColl = namedtuple("NamedColl", "a b c")


class TD(TypedDict):
    a: int
    b: int
    c: int


def make_dict():
    return {"a": 1, "b": 2, "c": 3}


kinds = [("dataclass", "DC(1, 2, 3)"),
         ("dataclass(slots=True)", "DCSlots(1, 2, 3)"),
         ("dataclass(frozen=True)", "DCFrozen(1, 2, 3)"),
         ("dataclass(frozen, slots)", "DCFrozenSlots(1, 2, 3)"),
         ("typing.NamedTuple", "NT(1, 2, 3)"),
         ("collections.namedtuple", "NamedColl(1, 2, 3)"),
         ("dict", "make_dict()"),
         ("TypedDict", "TD(a=1, b=2, c=3)")]
ns = dict(DC=DC, DCSlots=DCSlots, DCFrozen=DCFrozen, DCFrozenSlots=DCFrozenSlots,
          NT=NT, NamedColl=NamedColl, TD=TD, make_dict=make_dict)

print("criação (3 campos):")
for label, statement in kinds:
    seconds = min(timeit.repeat(statement, globals=ns, number=200_000, repeat=5)) / 200_000
    print(f"  {label:<26}{seconds * 1e9:7.1f} ns")


def traced(factory, n=50_000):
    tracemalloc.start()
    kept = [factory(i) for i in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current / n


print("memória por objeto (bytes, inclui os ints):")
for label, factory in [("dataclass", lambda i: DC(i, i, i)),
                       ("dataclass(slots=True)", lambda i: DCSlots(i, i, i)),
                       ("NamedTuple", lambda i: NT(i, i, i)),
                       ("dict", lambda i: {"a": i, "b": i, "c": i})]:
    print(f"  {label:<26}{traced(factory):7.0f}")
