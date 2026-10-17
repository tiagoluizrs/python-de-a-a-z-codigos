"""Exercício 2: curry simples com functools.partial (gabarito)."""
import functools
import inspect


def curry(func):
    sig = inspect.signature(func)
    # parâmetros que precisam ser fornecidos por posição
    needed = sum(
        1 for p in sig.parameters.values()
        if p.default is p.empty
        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD))

    def curried(*args):
        if len(args) >= needed:
            return func(*args)
        # faltam argumentos: partial fixa os recebidos e devolve
        # uma nova função que espera os demais
        return functools.partial(curried, *args)

    return curried
