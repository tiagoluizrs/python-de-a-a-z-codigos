"""Janelas deslizantes com deque e generator."""
from collections import deque
from itertools import islice


def windowed(iterable, size):
    it = iter(iterable)
    window = deque(islice(it, size), maxlen=size)
    if len(window) == size:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)


print(list(windowed("abcde", 3)))
print(list(windowed("ab", 3)))
