"""Gabarito do exercício 2."""
import functools
import inspect


def compose(*funcs):
    if not funcs:
        return lambda value: value
    *rest, first = funcs

    def composed(*args, **kwargs):
        result = first(*args, **kwargs)
        for func in reversed(rest):
            result = func(result)
        return result

    return composed


def pipe(value, *funcs):
    return functools.reduce(lambda acc, func: func(acc), funcs, value)


def curry(func):
    required = [p for p in inspect.signature(func).parameters.values()
                if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    arity = len(required)

    def collect(received):
        def step(*args):
            joined = received + args
            if len(joined) >= arity:
                return func(*joined)
            return collect(joined)
        return step

    return collect(())
