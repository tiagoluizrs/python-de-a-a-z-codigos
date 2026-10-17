"""Gabarito do exercício 2."""
import functools
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            # finally roda com sucesso OU com exceção
            wrapper.last_elapsed = time.perf_counter() - start

    wrapper.last_elapsed = None   # atributo da função-wrapper
    return wrapper


def retry(times, exceptions=(Exception,), delay=0.1, backoff=2.0,
          sleep=time.sleep):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise          # esgotou: propaga a última
                    sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator
