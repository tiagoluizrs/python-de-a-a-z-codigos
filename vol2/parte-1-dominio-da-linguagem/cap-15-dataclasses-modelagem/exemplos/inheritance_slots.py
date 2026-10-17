"""Herança de dataclasses, kw_only e slots."""
import sys
import tracemalloc
from dataclasses import dataclass


@dataclass
class Base:
    id: int
    created: str = "hoje"


# Sem kw_only, um campo obrigatório após o padrão falha
try:
    @dataclass
    class Child(Base):
        name: str
except TypeError as error:
    print("TypeError:", error)


@dataclass(kw_only=True)
class KwChild(Base):
    name: str                                            # obrigatório, só por nome


print(KwChild(1, name="x"), KwChild(id=2, name="y", created="ontem"))


@dataclass
class Extended(Base):
    extra: str = "-"


print(Extended(1, "ontem", "z"))


# slots=True (3.10+): gera __slots__ a partir dos campos
@dataclass
class Plain:
    x: int
    y: int


@dataclass(slots=True)
class Slotted:
    x: int
    y: int


print(hasattr(Plain(1, 2), "__dict__"), hasattr(Slotted(1, 2), "__dict__"), Slotted.__slots__)


def traced(cls, n=100_000):
    tracemalloc.start()
    kept = [cls(i, i) for i in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current / 1e6


print(f"100 mil objetos: comum {traced(Plain):.1f} MB | slots=True {traced(Slotted):.1f} MB")
