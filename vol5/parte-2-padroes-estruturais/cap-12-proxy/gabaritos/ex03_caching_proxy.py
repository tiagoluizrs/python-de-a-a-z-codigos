"""Gabarito do exercício 3."""
import functools
import time


class CachingProxy:
    def __init__(self, target, methods, ttl=None, clock=time.monotonic):
        for name in methods:
            if not hasattr(target, name):
                raise AttributeError(name)
            if not callable(getattr(target, name)):
                raise ValueError(f"não é um método: {name}")
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_methods", frozenset(methods))
        object.__setattr__(self, "_ttl", ttl)
        object.__setattr__(self, "_clock", clock)
        object.__setattr__(self, "_cache", {})
        object.__setattr__(self, "_stats", {"hits": 0, "misses": 0, "bypassed": 0})

    def __getattr__(self, name):
        attribute = getattr(self._target, name)
        if name not in self._methods:
            return attribute

        @functools.wraps(attribute)
        def cached(*args, **kwargs):
            key = (name, args, tuple(sorted(kwargs.items())))
            try:
                hash(key)
            except TypeError:
                self._stats["bypassed"] += 1
                return attribute(*args, **kwargs)
            entry = self._cache.get(key)
            if entry is not None and (self._ttl is None or self._clock() - entry[0] < self._ttl):
                self._stats["hits"] += 1
                return entry[1]
            self._stats["misses"] += 1
            value = attribute(*args, **kwargs)
            self._cache[key] = (self._clock(), value)
            return value

        return cached

    def invalidate(self, method=None):
        keys = [k for k in self._cache if method is None or k[0] == method]
        for key in keys:
            del self._cache[key]
        return len(keys)

    @property
    def stats(self):
        return dict(self._stats)
