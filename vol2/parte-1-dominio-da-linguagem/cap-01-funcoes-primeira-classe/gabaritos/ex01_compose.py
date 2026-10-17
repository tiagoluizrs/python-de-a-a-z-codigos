"""Exercício 1: composição de funções e pipeline (gabarito)."""
from functools import reduce


def compose(*funcs):
    if not funcs:
        return lambda x: x
    *rest, last = funcs

    def composed(*args, **kwargs):
        # a última função recebe os argumentos originais; o resultado
        # sobe pela cadeia de funções, da direita para a esquerda
        result = last(*args, **kwargs)
        return reduce(lambda acc, fn: fn(acc), reversed(rest), result)

    return composed


def pipe(value, *funcs):
    # reduce aplica cada função ao acumulador
    return reduce(lambda acc, fn: fn(acc), funcs, value)
