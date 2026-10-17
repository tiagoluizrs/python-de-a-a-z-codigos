"""Gabarito do exercício 4."""
import functools


def stack(fn, *decorators):
    for decorator in reversed(decorators):
        fn = decorator(fn)
    return fn


def labeled(name, log):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            log.append(f"entra {name}")
            try:
                return fn(*args, **kwargs)
            finally:
                log.append(f"sai {name}")

        return wrapper

    return decorator


def explain_order(names):
    log = []

    def f():
        log.append("f")

    stack(f, *[labeled(n, log) for n in names])()
    return log


def unwrap_chain(fn):
    chain = [fn]
    while hasattr(chain[-1], "__wrapped__"):
        chain.append(chain[-1].__wrapped__)
    return chain


def count_layers(fn):
    return len(unwrap_chain(fn)) - 1
