"""O custo de cada forma de garantir a limpeza."""
import timeit
from contextlib import contextmanager


class Plain:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@contextmanager
def gen_cm():
    yield


plain = Plain()


def nothing():
    x = 1
    return x


def with_try_finally():
    try:
        x = 1
    finally:
        pass
    return x


def with_class():
    with plain:
        x = 1
    return x


def with_generator():
    with gen_cm():
        x = 1
    return x


for func in (nothing, with_try_finally, with_class, with_generator):
    seconds = min(timeit.repeat(func, number=300_000, repeat=5)) / 300_000
    print(f"{func.__name__:<18}{seconds * 1e9:8.1f} ns")
