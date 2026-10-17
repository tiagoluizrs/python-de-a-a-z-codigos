"""Gabarito do exercício 2."""
from collections.abc import Sequence


class ArithSeq(Sequence):
    def __init__(self, start, step, length):
        self.start, self.step, self.length = start, step, length

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        if isinstance(index, slice):
            positions = range(*index.indices(self.length))     # índices resolvidos
            return ArithSeq(self.start + positions.start * self.step,
                            self.step * positions.step,
                            len(positions))
        if not -self.length <= index < self.length:
            raise IndexError("index out of range")
        index %= self.length                                    # índice negativo
        return self.start + index * self.step

    def __repr__(self):
        return f"ArithSeq({self.start!r}, {self.step!r}, {self.length!r})"
