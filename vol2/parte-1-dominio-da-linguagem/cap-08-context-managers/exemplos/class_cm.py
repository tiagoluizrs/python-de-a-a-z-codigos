"""Gerenciadores de contexto escritos como classes."""
import time


class Timer:
    """Mede o tempo do bloco; a exceção, se houver, continua."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False


with Timer() as timer:
    sum(range(1_000_000))
print(f"elapsed={timer.elapsed * 1e3:.1f} ms")


class Transaction:
    """Desfaz as mudanças se o bloco levantar uma exceção."""

    def __init__(self, store):
        self.store = store

    def __enter__(self):
        self.snapshot = dict(self.store)
        return self.store

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.store.clear()
            self.store.update(self.snapshot)       # rollback
        return False                                # a exceção continua


data = {"saldo": 100}
try:
    with Transaction(data) as tx:
        tx["saldo"] -= 30
        print("dentro:", data)
        raise RuntimeError("falha no meio")
except RuntimeError:
    print("depois do erro:", data)

with Transaction(data) as tx:
    tx["saldo"] += 5
print("commit:", data)


class Ignore:
    """Retornar True do __exit__ SUPRIME a exceção."""

    def __init__(self, *types):
        self.types = types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return exc_type is not None and issubclass(exc_type, self.types)


with Ignore(KeyError):
    {}["x"]
print("KeyError suprimida")

try:
    with Ignore(KeyError):
        1 / 0
except ZeroDivisionError:
    print("ZeroDivisionError não era para ignorar: continuou")


# Uma exceção dentro do __exit__ substitui a original (com contexto)
class Faulty:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        raise OSError("falha ao liberar")


try:
    with Faulty():
        raise ValueError("do corpo")
except OSError as error:
    print(type(error).__name__, "| context:", repr(error.__context__))
