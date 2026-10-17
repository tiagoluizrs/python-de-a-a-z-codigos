"""Funções de trabalho. Processos novos (spawn) precisam IMPORTAR a função pelo nome do módulo."""
import collections
import os
import time


def cpu_sum(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


def square(x):
    return x * x


def pid(_=None):
    return os.getpid()


def slow(seconds):
    time.sleep(seconds)
    return seconds


def fail(x):
    if x == 3:
        raise ValueError(f"item {x} é inválido")
    return x


def crash(_=None):
    os._exit(7)


def count_words(text):
    return collections.Counter(text.lower().split())


def increment(value, lock, n):
    for _ in range(n):
        with lock:
            value.value += 1


def child_main(out, func, args):
    """Corpo do processo filho de run_isolated: roda func e devolve ("ok", valor) ou ("error", exceção)."""
    try:
        out.put(("ok", func(*args)))
    except BaseException as error:         # noqa: BLE001
        out.put(("error", error))


def read_shared(name, size):
    from multiprocessing import shared_memory
    block = shared_memory.SharedMemory(name=name)
    try:
        return sum(block.buf[:size])
    finally:
        block.close()
