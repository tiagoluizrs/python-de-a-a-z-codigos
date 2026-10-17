"""Gabarito do exercício 1."""
import functools
from collections import OrderedDict, namedtuple

CacheInfo = namedtuple("CacheInfo", "hits misses maxsize currsize")


def memoize(maxsize=128):
    def decorate(func):
        cache = OrderedDict()
        stats = {"hits": 0, "misses": 0}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                cache.move_to_end(key)
                stats["hits"] += 1
                return cache[key]
            stats["misses"] += 1
            result = func(*args, **kwargs)
            cache[key] = result
            if maxsize is not None and len(cache) > maxsize:
                cache.popitem(last=False)
            return result

        def cache_info():
            return CacheInfo(stats["hits"], stats["misses"], maxsize, len(cache))

        def cache_clear():
            cache.clear()
            stats["hits"] = stats["misses"] = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper

    return decorate
