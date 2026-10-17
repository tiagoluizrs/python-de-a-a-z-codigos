"""Exercício 2: implementar a linearização C3 (o MRO) do zero."""


def c3_linearization(cls):
    """Calcule o MRO de ``cls`` SEM usar ``cls.__mro__``.

    Use apenas ``cls.__bases__`` e recursão (o MRO das bases). Algoritmo:

    ``L[C] = [C] + merge(L[B1], L[B2], ..., [B1, B2, ...])``

    ``merge`` repete: pegue o primeiro elemento da primeira lista cujo
    cabeça NÃO aparece na CAUDA de nenhuma outra lista; acrescente-o ao
    resultado e remova-o de todas as listas. Se nenhuma cabeça serve,
    levante ``TypeError("inconsistent hierarchy")``.

    Devolva uma lista de classes, igual a ``list(cls.__mro__)``.
    """
    raise NotImplementedError
