"""Gabarito do exercício 2."""
import functools
import weakref
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Color:
    r: int
    g: int
    b: int

    def __post_init__(self):
        for name in ("r", "g", "b"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255:
                raise ValueError(f"componente inválido: {name}={value!r}")


class ColorPool:
    def __init__(self, maxsize=128):
        if maxsize < 1:
            raise ValueError("maxsize deve ser >= 1")
        self._make = functools.lru_cache(maxsize=maxsize)(lambda r, g, b: Color(r, g, b))

    def color(self, r, g, b):
        return self._make(r, g, b)

    def info(self):
        i = self._make.cache_info()
        return {"hits": i.hits, "misses": i.misses, "size": i.currsize, "maxsize": i.maxsize}

    def clear(self):
        self._make.cache_clear()


class WeakPool:
    def __init__(self, factory):
        self._factory = factory
        self._pool = weakref.WeakValueDictionary()
        self._created = 0
        self._reused = 0

    def get(self, key):
        obj = self._pool.get(key)
        if obj is not None:
            self._reused += 1
            return obj
        obj = self._factory(key)
        self._pool[key] = obj
        self._created += 1
        return obj

    def __len__(self):
        return len(self._pool)

    def __contains__(self, key):
        return key in self._pool

    @property
    def stats(self):
        return {"created": self._created, "reused": self._reused}
