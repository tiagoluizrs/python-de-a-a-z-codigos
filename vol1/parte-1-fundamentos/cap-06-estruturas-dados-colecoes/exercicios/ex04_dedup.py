"""Exercício 4: remover duplicatas preservando a ordem."""
from collections.abc import Callable, Iterable


def dedup(items: Iterable, key: Callable | None = None) -> list:
    """Remova duplicatas mantendo a PRIMEIRA ocorrência e a ordem original.

    Se ``key`` for dada, dois itens são duplicados quando ``key(a) == key(b)``
    (a chave precisa ser hasheável), o que permite tratar itens não
    hasheáveis: ``dedup([[1], [2], [1]], key=tuple)`` devolve ``[[1], [2]]``.

    ``dedup("banana")`` devolve ``["b", "a", "n"]``.
    """
    raise NotImplementedError
