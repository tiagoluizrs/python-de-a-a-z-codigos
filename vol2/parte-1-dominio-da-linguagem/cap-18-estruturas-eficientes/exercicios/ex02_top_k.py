"""Exercício 2: os k maiores de um fluxo, em memória O(k)."""


class TopK:
    """Mantém apenas os ``k`` maiores valores vistos, com um min-heap de
    tamanho no máximo ``k`` (``heapq``); nunca guarda o fluxo inteiro.

    * ``TopK(k)`` (``k < 1`` levanta ``ValueError``);
    * ``add(value)``: considera um valor;
    * ``result()``: lista dos maiores, do MAIOR para o menor (cópia);
    * ``len(top)``: quantos estão guardados (no máximo ``k``).
    """

    def __init__(self, k):
        raise NotImplementedError


def merge_sorted_streams(*streams):
    """Mescla fluxos JÁ ordenados em uma lista ordenada, usando
    ``heapq.merge``. Sem fluxos, devolve ``[]``."""
    raise NotImplementedError
