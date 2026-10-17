"""Gabarito 4: take, windowed e moving_average."""
from collections import deque
from itertools import islice


def take(n, iterable):
    # islice não consome além de n itens de um iterador
    return list(islice(iterable, n))


def windowed(iterable, size):
    if size < 1:
        raise ValueError("size must be >= 1")
    it = iter(iterable)
    # maxlen descarta automaticamente o item mais antigo
    window = deque(islice(it, size), maxlen=size)
    if len(window) < size:
        return
    yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)


def moving_average(values, size):
    for window in windowed(values, size):
        yield sum(window) / size
