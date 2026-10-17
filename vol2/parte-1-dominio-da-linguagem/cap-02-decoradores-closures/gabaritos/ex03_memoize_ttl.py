"""Gabarito do exercício 3."""
import functools
import time


def memoize(ttl, clock=time.monotonic):
    def decorator(func):
        store = {}   # chave -> (momento_de_criação, valor)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # sorted() torna a ordem dos nomeados irrelevante
            key = (args, tuple(sorted(kwargs.items())))
            now = clock()
            entry = store.get(key)
            if entry is not None and now - entry[0] < ttl:
                return entry[1]
            value = func(*args, **kwargs)   # se falhar, nada é guardado
            store[key] = (now, value)
            return value

        wrapper.cache_clear = store.clear
        wrapper.cache_size = lambda: len(store)
        return wrapper
    return decorator
