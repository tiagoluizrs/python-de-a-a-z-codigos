"""Exercício 1: composição de funções e pipeline."""


def compose(*funcs):
    """Componha funções da direita para a esquerda.

    ``compose(f, g, h)(x)`` equivale a ``f(g(h(x)))``. A função
    resultante aceita os argumentos que a ÚLTIMA função aceitar
    (as demais recebem um único valor). Sem funções, devolva a
    identidade. Dica: ``functools.reduce``.

    >>> compose(str, abs)(-3)
    '3'
    >>> compose()(5)
    5
    """
    raise NotImplementedError


def pipe(value, *funcs):
    """Passe ``value`` por ``funcs`` da esquerda para a direita.

    >>> pipe(" Hello ", str.strip, str.lower, len)
    5
    """
    raise NotImplementedError
