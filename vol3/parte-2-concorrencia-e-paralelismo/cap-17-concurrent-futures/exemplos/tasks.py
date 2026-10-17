"""Funções de trabalho importáveis (processos e subinterpretadores precisam importar pelo nome)."""
import os
import time


def square(x):
    return x * x


def cpu_sum(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


def slow(seconds):
    time.sleep(seconds)
    return seconds


def fail(x):
    if x == 2:
        raise ValueError(f"item {x} é inválido")
    return x


def crash(_=None):
    os._exit(7)


def pid(_=None):
    return os.getpid()


def apply_batch(func, batch):
    return [func(item) for item in batch]
