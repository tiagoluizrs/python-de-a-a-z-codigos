"""Funções de trabalho importáveis."""


def cpu_sum(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


def sum_squares(chunk):
    return sum(x * x for x in chunk)
