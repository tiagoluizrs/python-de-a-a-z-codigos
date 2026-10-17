"""Iteravel x iterador: o protocolo completo."""
from collections.abc import Iterable, Iterator


class Countdown:
    """Iterador escrito a mao: serve a si mesmo (uma passada)."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class Playlist:
    """Iteravel: cada iter() devolve um iterador novo."""

    def __init__(self, songs):
        self.songs = list(songs)

    def __iter__(self):
        return iter(self.songs)


c = Countdown(3)
print(list(c), list(c))              # segunda passada vazia
p = Playlist(["a", "b"])
print(list(p), list(p))              # reutilizavel
print(iter(c) is c, iter(p) is p)

print(isinstance(c, Iterator), isinstance(p, Iterator))
print(isinstance(p, Iterable), isinstance([], Iterator))
print(isinstance(iter([]), Iterator), isinstance(5, Iterable))


# protocolo antigo: so __getitem__
class Legacy:
    def __getitem__(self, index):
        if index >= 3:
            raise IndexError(index)
        return index * 10


print(list(Legacy()), isinstance(Legacy(), Iterable))
print(type(iter(Legacy())).__name__)

# iter(callable, sentinela)
values = iter([3, 2, 1, 0, 9])
print(list(iter(lambda: next(values), 0)))

# StopIteration manual
it = iter([1])
print(next(it))
try:
    next(it)
except StopIteration as exc:
    print("StopIteration", repr(exc.value))
print(next(it, "default"))

# __length_hint__
import operator
print(operator.length_hint(iter([1, 2, 3])))
print(operator.length_hint(x for x in range(3)))
print(operator.length_hint(x for x in range(3)), "default 7 ->",
      operator.length_hint((x for x in range(3)), 7))
li = iter([1, 2, 3])
next(li)
print(li.__length_hint__())
print(list(map(len, ["a", "bb"])).__len__())


class Sized:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return iter(range(self.n))

    def __length_hint__(self):
        return self.n


print(operator.length_hint(Sized(42)))
