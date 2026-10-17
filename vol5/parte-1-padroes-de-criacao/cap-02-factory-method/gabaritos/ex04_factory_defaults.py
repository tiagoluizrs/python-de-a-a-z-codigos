"""Gabarito do exercício 4."""
import copy
import inspect


def factory_for(cls, **defaults):
    params = inspect.signature(cls).parameters
    accepts_any = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())

    def check(names):
        if accepts_any:
            return
        for name in names:
            if name not in params:
                raise TypeError(f"{cls.__name__} não aceita o argumento {name!r}")

    check(defaults)
    stored = copy.deepcopy(defaults)

    def make(**overrides):
        check(overrides)
        return cls(**{**copy.deepcopy(stored), **overrides})

    make.cls = cls
    make.defaults = copy.deepcopy(stored)
    return make
