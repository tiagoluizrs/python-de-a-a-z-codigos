"""Gabarito do exercício 2."""
from contextlib import contextmanager


@contextmanager
def transaction(store):
    snapshot = dict(store)
    try:
        yield store
    except BaseException:
        store.clear()
        store.update(snapshot)          # rollback no MESMO dict
        raise                            # relança: o chamador precisa saber


class _Counter:
    def __init__(self):
        self.count = 0


@contextmanager
def suppress_and_count(*exception_types):
    counter = _Counter()
    try:
        yield counter
    except exception_types:
        counter.count += 1              # suprimida: o gerador a trata e termina
