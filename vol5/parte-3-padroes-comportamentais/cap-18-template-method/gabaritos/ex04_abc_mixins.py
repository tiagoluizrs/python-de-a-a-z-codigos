"""Gabarito do exercício 4."""
from collections.abc import Mapping, MutableSet, Sequence


class Countdown(Sequence):
    def __init__(self, start):
        if start < 0:
            raise ValueError("start negativo")
        self.start = start

    def __len__(self):
        return self.start + 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self)))]
        if index < 0:
            index += len(self)
        if not 0 <= index < len(self):
            raise IndexError(index)
        return self.start - index


class CaseInsensitiveMap(Mapping):
    def __init__(self, data):
        self._data, self._lookup = {}, {}
        for key, value in data.items():
            folded = key.casefold()
            if folded in self._lookup:
                raise ValueError(f"chave duplicada: {key}")
            self._lookup[folded] = key
            self._data[key] = value

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise KeyError(key)
        return self._data[self._lookup[key.casefold()]]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class OrderedSet(MutableSet):
    def __init__(self, items=()):
        self._d = dict.fromkeys(items)

    def __contains__(self, item):
        return item in self._d

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def add(self, item):
        self._d[item] = None

    def discard(self, item):
        self._d.pop(item, None)

    @classmethod
    def _from_iterable(cls, it):
        return cls(it)

    def __repr__(self):
        return f"OrderedSet({list(self._d)})"
