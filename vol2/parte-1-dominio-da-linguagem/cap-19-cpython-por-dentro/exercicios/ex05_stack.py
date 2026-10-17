"""Exercício 5: percorrer a pilha de chamadas."""


def caller_names():
    """Nomes das funções que estão na pilha ACIMA de quem chamou esta função,
    do chamador imediato até o mais externo. Use ``sys._getframe``.

    ``def a(): return b()`` / ``def b(): return caller_names()`` chamando
    ``a()`` devolve uma lista que COMEÇA com ``["b", "a"]`` (pode continuar
    com os quadros do chamador, como o teste)."""
    raise NotImplementedError


def recursion_capacity():
    """Quantas chamadas recursivas simples uma função consegue empilhar antes
    de ``RecursionError``, medido na prática (``int``). Restaure qualquer
    mudança que fizer em ``sys.setrecursionlimit``."""
    raise NotImplementedError


def calling_line():
    """Número da linha, no ARQUIVO do chamador, em que ``calling_line()`` foi
    chamada (``f_lineno`` do quadro do chamador)."""
    raise NotImplementedError
