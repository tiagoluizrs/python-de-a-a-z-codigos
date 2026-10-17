"""Gabarito do exercício 5."""
import functools
import inspect
import typing


def validate_types(func):
    sig = inspect.signature(func)
    # Lido UMA vez, na decoração (não a cada chamada)
    hints = typing.get_type_hints(func)
    hints.pop("return", None)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)   # TypeError se não casar
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            expected = hints.get(name)
            # só validamos classes simples; int | None etc. passam
            if isinstance(expected, type) and \
                    not isinstance(value, expected):
                raise TypeError(
                    f"{name} must be {expected.__name__}, "
                    f"got {type(value).__name__}")
        return func(*args, **kwargs)
    return wrapper
