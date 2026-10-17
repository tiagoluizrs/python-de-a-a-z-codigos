"""Padrões defensivos contra mutabilidade compartilhada."""
from dataclasses import FrozenInstanceError, dataclass, field
from types import MappingProxyType


# 1) Copiar na entrada e expor só leitura na saída
class Team:
    def __init__(self, members: list[str]) -> None:
        self._members = list(members)        # cópia na entrada

    @property
    def members(self) -> tuple[str, ...]:
        return tuple(self._members)          # cópia imutável na saída


names = ["ana", "bia"]
team = Team(names)
names.append("caio")                         # não afeta o time
print(team.members)
try:
    team.members.append("x")                 # type: ignore[attr-defined]
except AttributeError as exc:
    print("AttributeError:", exc)


# 2) Dataclass congelada: o 'frozen' é RASO
@dataclass(frozen=True)
class Config:
    name: str
    flags: frozenset[str] = frozenset()
    extras: list[str] = field(default_factory=list)   # armadilha


cfg = Config("app", frozenset({"a"}))
try:
    cfg.name = "other"
except FrozenInstanceError as exc:
    print("FrozenInstanceError:", exc)
cfg.extras.append("ainda muta")              # o frozen não protege isto
print(cfg.extras)
print("hasheável só se todos os campos forem:", end=" ")
try:
    hash(cfg)
except TypeError as exc:
    print(exc)

# 3) Visão somente leitura de um dict
settings = {"debug": False}
view = MappingProxyType(settings)
try:
    view["debug"] = True                     # type: ignore[index]
except TypeError as exc:
    print("TypeError:", exc)
settings["debug"] = True                     # o original muda...
print("a visão acompanha:", view["debug"])   # ...e a visão enxerga


# 4) Estrutura persistente (conceito): compartilha o que não mudou
@dataclass(frozen=True)
class Stack:
    head: object = None
    tail: "Stack | None" = None

    def push(self, value) -> "Stack":
        return Stack(value, self)


empty = Stack()
s1 = empty.push("a")
s2 = s1.push("b")
s3 = s1.push("c")                            # ramifica a partir de s1
print("\ns2 e s3 compartilham a base:", s2.tail is s3.tail is s1)
