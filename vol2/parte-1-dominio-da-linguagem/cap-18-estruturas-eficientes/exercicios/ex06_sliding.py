"""Exercício 6: janelas deslizantes com deque."""


def moving_average(values, size):
    """Gerador das médias móveis de janelas COMPLETAS de ``size`` itens
    (``float``). ``size < 1`` levanta ``ValueError`` (ao ITERAR, por ser
    gerador, ou ao chamar; os testes iteram). Mantenha a soma corrente: cada
    item entra e sai da janela uma vez (O(n) total). ``values`` pode ser um
    iterável qualquer."""
    raise NotImplementedError


def max_sliding_window(numbers, size):
    """Máximo de cada janela de ``size`` itens, em O(n), com um ``deque`` de
    ÍNDICES em ordem decrescente de valor (a técnica da "fila monotônica").
    ``max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)`` ->
    ``[3, 3, 5, 5, 6, 7]``. ``size`` maior que a lista devolve ``[]``."""
    raise NotImplementedError
