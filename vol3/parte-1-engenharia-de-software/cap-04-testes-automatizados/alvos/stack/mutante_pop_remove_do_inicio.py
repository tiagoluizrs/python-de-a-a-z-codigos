"""Alvo do exercício 2."""


class EmptyStackError(Exception):
    """Operação em pilha vazia."""


class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise EmptyStackError("pilha vazia")
        return self._items.pop(0)

    def peek(self):
        if not self._items:
            raise EmptyStackError("pilha vazia")
        return self._items[-1]

    def __len__(self):
        return len(self._items)

    def is_empty(self):
        return len(self._items) == 0
