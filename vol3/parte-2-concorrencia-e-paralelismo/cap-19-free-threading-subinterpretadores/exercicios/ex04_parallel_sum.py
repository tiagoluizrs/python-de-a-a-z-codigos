"""Exercício 4: a mesma soma em threads, processos ou subinterpretadores."""


def split(data, parts):
    """Divide ``data`` (sequência) em exatamente ``parts`` pedaços consecutivos de
    tamanhos que diferem em no máximo 1 (os maiores primeiro). ``parts < 1`` levanta
    ``ValueError``."""
    raise NotImplementedError


def sum_squares_parallel(data, workers=2, kind="thread"):
    """Soma dos quadrados de ``data``: divida em ``workers`` pedaços (``split``) e
    execute ``tasks.sum_squares(pedaço)`` (módulo ``tasks``, importável) em um
    executor de ``concurrent.futures``: ``kind`` é ``"thread"``, ``"process"`` ou
    ``"interpreter"`` (outro valor levanta ``ValueError``). Devolve a soma total;
    ``data`` vazio devolve 0 sem criar executor."""
    raise NotImplementedError
