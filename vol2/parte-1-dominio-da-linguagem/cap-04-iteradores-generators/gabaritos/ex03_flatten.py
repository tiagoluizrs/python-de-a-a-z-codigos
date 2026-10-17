"""Gabarito 3: flatten recursivo com yield from."""
from collections.abc import Iterable


def _is_container(obj):
    # str e bytes são iteráveis de si mesmos: seriam recursão infinita
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes))


def flatten(items):
    for item in items:
        if _is_container(item):
            yield from flatten(item)   # delega ao subgerador
        else:
            yield item


def depth_of(items):
    if not _is_container(items):
        return 0
    # default=0 cobre o contêiner vazio; somamos 1 pelo nível atual
    return 1 + max((depth_of(item) for item in items), default=0)
