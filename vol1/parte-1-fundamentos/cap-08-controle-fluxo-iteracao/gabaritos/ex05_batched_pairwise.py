"""Gabarito do exercício 5 (usando generators, adiantando o Cap. 4 do Volume 2)."""
from itertools import islice


def my_batched(iterable, n: int, *, strict: bool = False):
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)      # funciona até com iteradores
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


def my_pairwise(iterable):
    iterator = iter(iterable)
    try:
        previous = next(iterator)
    except StopIteration:
        return                     # vazio: nenhum par
    for current in iterator:       # continua de onde o next parou
        yield previous, current
        previous = current
