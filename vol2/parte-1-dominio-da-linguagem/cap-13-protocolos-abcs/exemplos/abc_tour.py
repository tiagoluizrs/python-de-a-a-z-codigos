"""collections.abc: interfaces estruturais e as que exigem herança/registro."""
from collections import abc


class Sized3:
    def __len__(self):
        return 3


class Iter3:
    def __iter__(self):
        return iter(range(3))


class Call3:
    def __call__(self):
        return 3


class Hash3:
    def __hash__(self):
        return 3


# ABCs de UM método: o isinstance é ESTRUTURAL (basta ter o método)
for obj, ABC in [(Sized3(), abc.Sized), (Iter3(), abc.Iterable),
                 (Call3(), abc.Callable), (Hash3(), abc.Hashable),
                 (Sized3(), abc.Iterable)]:
    print(f"{type(obj).__name__:<7} é {ABC.__name__:<9}? {isinstance(obj, ABC)}")
print("list é Hashable?", isinstance([], abc.Hashable), "| tuple?", isinstance((), abc.Hashable))


# Sequence NÃO é estrutural: exige herança (ou register)
class Fake:
    """Tem __getitem__ e __len__, mas não herda de Sequence."""

    def __len__(self):
        return 3

    def __getitem__(self, i):
        return i * 10


print("Fake é Sequence?", isinstance(Fake(), abc.Sequence))


class Countdown(abc.Sequence):
    """Implementa APENAS __len__ e __getitem__; o resto vem de graça."""

    def __init__(self, start):
        self.start = start

    def __len__(self):
        return self.start

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self)))]
        if not -len(self) <= index < len(self):
            raise IndexError(index)
        return self.start - (index % len(self))


cd = Countdown(5)
print(list(cd), cd[1:4], 3 in cd, cd.index(2), cd.count(4))
print(list(reversed(cd)), isinstance(cd, abc.Sequence), isinstance(cd, abc.Iterable))
inherited = ("index", "count", "__contains__", "__iter__", "__reversed__")
print("herdados de Sequence (não escritos em Countdown):",
      [name for name in inherited if name not in vars(Countdown)])

# Registro: "declare" que uma classe de terceiros cumpre o contrato
abc.Sequence.register(Fake)
print("depois do register, Fake é Sequence?", isinstance(Fake(), abc.Sequence))

# Os dicionários e conjuntos
print(isinstance({}, abc.Mapping), isinstance({}, abc.MutableMapping),
      isinstance(frozenset(), abc.Set), isinstance(frozenset(), abc.MutableSet))
print(isinstance("abc", abc.Sequence), isinstance(b"ab", abc.Sequence),
      isinstance(range(3), abc.Sequence), isinstance({1}, abc.Sequence))
