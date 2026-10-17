"""Gabarito do exercício 4."""
from collections.abc import Callable, Iterator, Sequence
from typing import Protocol, Self


class Comparable(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> Self:
        self._items.append(item)
        return self

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pilha vazia")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("pilha vazia")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return reversed(self._items)


class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value

    def map[U](self, f: Callable[[T], U]) -> Box[U]:
        return Box(f(self.value))


def merge_sorted[C: Comparable](a: Sequence[C], b: Sequence[C]) -> list[C]:
    result: list[C] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if b[j] < a[i]:
            result.append(b[j])
            j += 1
        else:
            result.append(a[i])
            i += 1
    return result + list(a[i:]) + list(b[j:])
