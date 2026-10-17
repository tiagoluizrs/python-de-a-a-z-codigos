"""Exercício 4: ordenação por vários critérios."""


def sort_by(records, *keys):
    """Ordena uma lista de ``dict``s por várias chaves, na ordem dada.

    Cada chave é uma string: ``"age"`` (crescente) ou ``"-age"`` (decrescente).
    Use ordenações ESTÁVEIS em passadas e ``operator.itemgetter``; funciona
    com valores de qualquer tipo comparável (inclusive strings decrescentes).
    Devolve uma lista NOVA; a original não muda.
    """
    raise NotImplementedError


def sort_numbers_largest(numbers):
    """Dada uma lista de inteiros não negativos, devolve a ``str`` formada
    pela ordem que produz o MAIOR número ao concatenar
    (``[3, 30, 34, 5, 9]`` -> ``"9534330"``). Use ``functools.cmp_to_key``."""
    raise NotImplementedError
