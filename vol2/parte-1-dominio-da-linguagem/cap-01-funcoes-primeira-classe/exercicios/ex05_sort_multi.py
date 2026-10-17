"""Exercício 5: ordenar por vários critérios com itemgetter."""


def sort_staff(rows):
    """Ordene ``rows`` (lista de dicts) e devolva uma NOVA lista.

    Critérios, em ordem de prioridade:

    1. ``dept`` crescente;
    2. ``salary`` DECRESCENTE;
    3. ``name`` crescente.

    Não use ``lambda``: use ``operator.itemgetter``. Dica: a
    ordenação do Python é estável, então você pode ordenar em
    passos, do critério menos importante para o mais importante.
    Não altere a lista original.
    """
    raise NotImplementedError


def top_per_dept(rows):
    """Devolva ``{dept: nome}`` do funcionário de maior salário.

    Em caso de empate de salário, vale o menor nome. Dica: reaproveite
    ``sort_staff`` e percorra o resultado.
    """
    raise NotImplementedError
