"""Tarefas de teste, em um módulo IMPORTÁVEL (processos novos precisam importá-las pelo nome)."""
import time


def cpu_task(n=1_500_000):
    """Trabalho de CPU puro, em Python: não solta o GIL."""
    total = 0
    for i in range(n):
        total += i * i % 7
    return total


def io_task(seconds=0.1):
    """Espera de E/S simulada: o GIL é liberado durante o sleep."""
    time.sleep(seconds)
    return seconds


def mixed_task(n=300_000, seconds=0.05):
    """Um pouco de CPU e um pouco de espera."""
    total = cpu_task(n)
    time.sleep(seconds)
    return total


def square(x):
    return x * x
