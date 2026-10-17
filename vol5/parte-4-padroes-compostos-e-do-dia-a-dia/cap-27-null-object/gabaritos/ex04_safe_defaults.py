"""Gabarito do exercício 4."""
import contextlib
import logging
from collections.abc import Mapping


def names_of(users):
    return [user["name"] for user in users or ()]


def first_or(iterable, default=None):
    return next(iter(iterable or ()), default)


_MISSING = object()


def setting(config, path, default=None):
    current = config
    for step in path.split("."):
        if not isinstance(current, Mapping):
            return default
        current = current.get(step, _MISSING)
        if current is _MISSING:
            return default
    return current


def locked(lock=None):
    return lock if lock is not None else contextlib.nullcontext()


def quiet_logger(name):
    logger = logging.getLogger(name)
    logger.handlers = [logging.NullHandler()]
    logger.propagate = False
    return logger


def _noop(*args, **kwargs):
    return None


def run_tasks(tasks, on_progress=None):
    progress = on_progress if on_progress is not None else _noop
    tasks = list(tasks)
    results = []
    for i, task in enumerate(tasks, 1):
        results.append(task())
        progress(i, len(tasks), results[-1])
    return results
