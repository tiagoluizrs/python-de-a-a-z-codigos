"""Gabarito do exercício 4."""
import contextlib
import contextvars
import logging

CONTEXT = contextvars.ContextVar("log_context", default={})


@contextlib.contextmanager
def log_context(**fields):
    token = CONTEXT.set({**CONTEXT.get(), **fields})
    try:
        yield
    finally:
        CONTEXT.reset(token)


class ContextFilter(logging.Filter):
    def filter(self, record):
        context = CONTEXT.get()
        for key, value in context.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True
