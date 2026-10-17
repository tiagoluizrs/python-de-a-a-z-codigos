"""Gabarito do exercício 3."""
from contextlib import contextmanager

_MISSING = object()


@contextmanager
def transaction(store):
    backup = dict(store)
    try:
        yield store
    except BaseException:
        store.clear()
        store.update(backup)
        raise


@contextmanager
def temporary_attr(obj, name, value):
    old = getattr(obj, name, _MISSING)
    setattr(obj, name, value)
    try:
        yield obj
    finally:
        if old is _MISSING:
            delattr(obj, name)
        else:
            setattr(obj, name, old)


@contextmanager
def collect_errors(errors, *exceptions):
    caught = exceptions or (Exception,)
    try:
        yield errors
    except caught as error:
        errors.append(error)


@contextmanager
def ordered_cleanup(log, name):
    log.append(f"abrir {name}")
    try:
        yield name
    except BaseException as error:
        log.append(f"erro em {name}: {type(error).__name__}")
        raise
    finally:
        log.append(f"fechar {name}")


def run_steps(steps, log):
    results = []
    for name, fn in steps:
        with ordered_cleanup(log, name):
            results.append(fn())
    return results
