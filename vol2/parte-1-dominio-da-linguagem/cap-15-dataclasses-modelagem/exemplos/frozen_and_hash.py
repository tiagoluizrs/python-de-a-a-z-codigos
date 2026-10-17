"""frozen, eq e hash: quando o objeto pode ser chave de dict."""
import dataclasses
from dataclasses import dataclass, replace


@dataclass
class Plain:
    x: int


@dataclass(frozen=True)
class Frozen:
    x: int


@dataclass(eq=False)
class Identity:
    x: int


print("eq=True,  frozen=False:", Plain.__hash__)                 # None: não hasheável
print("eq=True,  frozen=True :", Frozen.__hash__ is not None)    # hash gerado
print("eq=False              :", Identity.__hash__ is object.__hash__)
try:
    {Plain(1): "a"}
except TypeError as error:
    print("TypeError:", error)
print({Frozen(1): "ok"}[Frozen(1)])

# Frozen: imutável (só o próprio objeto)
f = Frozen(1)
try:
    f.x = 2
except dataclasses.FrozenInstanceError as error:
    print("FrozenInstanceError:", error)


@dataclass(frozen=True)
class Bag:
    items: list


bag = Bag([1, 2])
bag.items.append(3)                                              # a lista continua mutável
print(bag)
try:
    hash(bag)
except TypeError as error:
    print("TypeError:", error)


# O jeito imutável de verdade: tuple e frozendict (3.15)
@dataclass(frozen=True)
class Safe:
    items: tuple
    extras: frozendict


safe = Safe((1, 2), frozendict(a=1))
print(hash(safe) == hash(Safe((1, 2), frozendict(a=1))), safe)

# replace: copia mudando campos (o jeito de "alterar" um objeto imutável)
g = replace(f, x=10)
print(f, g)


# __post_init__ em frozen: use object.__setattr__ para campos derivados
@dataclass(frozen=True)
class Circle:
    radius: float
    area: float = dataclasses.field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "area", 3.14159 * self.radius**2)


print(Circle(2))

# unsafe_hash=True: hash mesmo sem frozen (você promete não mutar)
@dataclass(unsafe_hash=True)
class Risky:
    x: int


print(hash(Risky(1)) == hash(Risky(1)))
