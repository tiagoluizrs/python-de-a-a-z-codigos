"""Gabarito do exercício 2."""
import functools
import warnings


def deprecated(since, removal, alternative=None):
    def decorate(func):
        message = f"{func.__name__} está obsoleta desde {since} e será removida na {removal}"
        if alternative:
            message += f"; use {alternative}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        wrapper.__doc__ = (func.__doc__ or "") + f"\n\nObsoleta desde {since}."
        return wrapper

    return decorate


def renamed_parameter(old, new, since):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if old in kwargs:
                if new in kwargs:
                    raise TypeError(f"não use {old!r} e {new!r} juntos")
                warnings.warn(f"parâmetro {old!r} foi renomeado para {new!r} na versão {since}", DeprecationWarning, stacklevel=2)
                kwargs[new] = kwargs.pop(old)
            return func(*args, **kwargs)

        return wrapper

    return decorate
