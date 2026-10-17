"""Gabarito do exercício 5."""


class BoundedStack:
    def __init__(self, capacity):
        self._capacity = capacity
        self._items = []                       # composição: a lista é detalhe interno

    def push(self, item):
        if len(self._items) >= self._capacity:
            raise OverflowError("pilha cheia")
        self._items.append(item)

    def pop(self):
        return self._items.pop()               # IndexError natural se vazia

    def peek(self):
        return self._items[-1]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return reversed(self._items)           # do topo para a base

    def __repr__(self):
        return f"BoundedStack({self._items!r}, capacity={self._capacity})"
