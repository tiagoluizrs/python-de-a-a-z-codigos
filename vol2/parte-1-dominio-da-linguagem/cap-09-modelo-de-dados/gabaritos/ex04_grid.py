"""Gabarito do exercício 4."""


class Grid:
    def __init__(self, rows, cols):
        self._cells = [[0] * cols for _ in range(rows)]

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            row, col = key
            return self._cells[row][col]                  # IndexError natural
        return list(self._cells[key])                     # cópia da linha

    def __setitem__(self, key, value):
        row, col = key
        self._cells[row][col] = value

    def __contains__(self, value):
        return any(value in row for row in self._cells)

    def __eq__(self, other):
        if not isinstance(other, Grid):
            return NotImplemented
        return self._cells == other._cells

    __hash__ = None                                       # mutável: não hasheável
