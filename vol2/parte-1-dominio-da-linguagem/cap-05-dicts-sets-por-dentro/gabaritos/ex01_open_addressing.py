"""Gabarito do exercício 1."""

_EMPTY = object()      # posição nunca usada
_TOMBSTONE = object()  # lápide: posição que já teve uma chave


class LinearProbingTable:
    def __init__(self):
        self.slots = 8
        self._table = [_EMPTY] * self.slots   # _EMPTY, _TOMBSTONE ou [chave, valor]
        self._used = 0                         # vivos + lápides
        self._size = 0                         # só vivos

    def _find(self, key):
        """Devolve (posição da chave ou None, posição reutilizável)."""
        index = hash(key) % self.slots
        reusable = None
        for _ in range(self.slots):
            cell = self._table[index]
            if cell is _EMPTY:
                return None, reusable if reusable is not None else index
            if cell is _TOMBSTONE:
                if reusable is None:
                    reusable = index           # pode reaproveitar a lápide
            elif cell[0] is key or cell[0] == key:
                return index, None
            index = (index + 1) % self.slots   # sondagem linear
        return None, reusable

    def _resize(self):
        live = [cell for cell in self._table
                if cell is not _EMPTY and cell is not _TOMBSTONE]
        self.slots *= 2
        self._table = [_EMPTY] * self.slots
        self._used = self._size = 0
        for key, value in live:               # a rehash descarta as lápides
            self[key] = value

    def __setitem__(self, key, value):
        found, free = self._find(key)
        if found is not None:
            self._table[found][1] = value
            return
        if (self._used + 1) * 3 > self.slots * 2:   # carga máxima: 2/3
            self._resize()
            found, free = self._find(key)
        if self._table[free] is _EMPTY:
            self._used += 1                    # lápide reutilizada não aumenta o uso
        self._table[free] = [key, value]
        self._size += 1

    def __getitem__(self, key):
        found, _ = self._find(key)
        if found is None:
            raise KeyError(key)
        return self._table[found][1]

    def __delitem__(self, key):
        found, _ = self._find(key)
        if found is None:
            raise KeyError(key)
        self._table[found] = _TOMBSTONE
        self._size -= 1

    def __contains__(self, key):
        return self._find(key)[0] is not None

    def __len__(self):
        return self._size

    def __iter__(self):
        for cell in self._table:
            if cell is not _EMPTY and cell is not _TOMBSTONE:
                yield cell[0]
