"""Exercício 4: ferramentas com bisect."""


def grade(score, breakpoints, labels):
    """Mapeia ``score`` para um rótulo com ``bisect``.

    ``breakpoints`` é uma lista ordenada de limites (o limite pertence à faixa
    de CIMA) e ``labels`` tem um item a mais que ``breakpoints``.
    ``grade(75, [60, 70, 80, 90], "FDCBA")`` -> ``"C"``; ``grade(90, ...)`` ->
    ``"A"``.
    """
    raise NotImplementedError


def insert_unique(sorted_list, value):
    """Insere ``value`` mantendo a lista ordenada e SEM duplicar. Devolve
    ``True`` se inseriu, ``False`` se já existia. Use ``bisect_left``."""
    raise NotImplementedError


def count_in_range(sorted_list, low, high):
    """Quantos itens de ``sorted_list`` estão em ``low <= x <= high``
    (intervalo fechado), em O(log n)."""
    raise NotImplementedError


def closest(sorted_list, target):
    """O valor de ``sorted_list`` mais próximo de ``target`` (em empate, o
    MENOR). Lista vazia levanta ``ValueError``."""
    raise NotImplementedError
