"""Exercício 4: genéricos com a sintaxe do 3.12.

Implemente (com tipos corretos para ``mypy --strict``):

* ``class Stack[T]``: ``push(item) -> Self`` (permite encadear), ``pop() -> T``
  (``IndexError("pilha vazia")`` se vazia), ``peek() -> T``, ``__len__``,
  ``__iter__`` (do topo para a base);
* ``class Box[T]``: guarda ``value: T``; ``map[U](f: Callable[[T], U]) ->
  Box[U]`` devolve uma NOVA caixa com ``f(value)``;
* ``merge_sorted[C: Comparable](a, b)``: mescla duas sequências JÁ ordenadas
  (``Sequence[C]``) em uma ``list[C]`` ordenada (estável: em empate, o item de
  ``a`` vem primeiro). ``Comparable`` é um ``Protocol`` com ``__lt__``.

A correção confere por ``reveal_type`` que ``Stack[int]().pop()`` é ``int`` e
``Box(3).map(str)`` é ``Box[str]``, e que ``merge_sorted`` recusa objetos sem ``<``.
"""
from collections.abc import Callable, Iterator, Sequence
from typing import Protocol, Self


class Comparable(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...


class Stack:
    pass


class Box:
    pass


def merge_sorted(a, b):
    raise NotImplementedError
