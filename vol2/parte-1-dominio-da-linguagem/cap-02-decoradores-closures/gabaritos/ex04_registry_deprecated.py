"""Gabarito do exercício 4."""
import functools
import warnings

PLUGINS = {}


def register(name):
    def decorator(func):
        if name in PLUGINS:
            raise ValueError(f"duplicate plugin: {name}")
        PLUGINS[name] = func
        return func      # devolve o original: custo zero na chamada
    return decorator


def run(name, *args, **kwargs):
    try:
        plugin = PLUGINS[name]
    except KeyError:
        raise KeyError(f"unknown plugin: {name}") from None
    return plugin(*args, **kwargs)


def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # stacklevel=2: o aviso aponta para quem CHAMOU wrapper
            warnings.warn(f"{func.__name__} is deprecated: {reason}",
                          DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
