"""Gabarito do exercício 2."""
import functools
import time
import warnings


def retry(times, exceptions=(Exception,), delay=0.0, sleep=time.sleep):
    if times < 1:
        raise ValueError("times deve ser >= 1")

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                wrapper.attempts = attempt
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    if delay > 0:
                        sleep(delay)

        wrapper.attempts = 0
        return wrapper

    return decorator


def timed(clock=time.perf_counter):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return fn(*args, **kwargs)
            finally:
                wrapper.durations.append(clock() - start)

        wrapper.durations = []
        wrapper.last = lambda: wrapper.durations[-1] if wrapper.durations else None
        return wrapper

    return decorator


def memoize(fn):
    cache = {}

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            wrapper.hits += 1
            return cache[key]
        result = fn(*args, **kwargs)
        wrapper.misses += 1
        cache[key] = result
        return result

    def cache_clear():
        cache.clear()
        wrapper.hits = wrapper.misses = 0

    wrapper.hits = wrapper.misses = 0
    wrapper.cache_clear = cache_clear
    return wrapper


def deprecated(message, *, warn=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            text = f"{fn.__name__} está obsoleta: {message}"
            if warn is not None:
                warn(text)
            else:
                warnings.warn(text, DeprecationWarning, stacklevel=2)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
