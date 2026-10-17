"""Gabarito do exercício 2."""
import json
import threading
import time


class CacheAside:
    def __init__(self, redis, loader, ttl_seconds=30, prefix="cache", lock_ms=2000):
        self.redis, self.loader, self.ttl, self.prefix, self.lock_ms = redis, loader, ttl_seconds, prefix, lock_ms
        self.hits = self.misses = 0
        self._counters = threading.Lock()

    def _count(self, name):
        with self._counters:
            setattr(self, name, getattr(self, name) + 1)

    def get(self, key):
        cache_key, lock_key = f"{self.prefix}:{key}", f"{self.prefix}:lock:{key}"
        waited = False
        while True:
            cached = self.redis.get(cache_key)
            if cached is not None:
                self._count("hits")
                return json.loads(cached)
            if self.redis.set(lock_key, "1", nx=True, px=self.lock_ms):
                try:
                    cached = self.redis.get(cache_key)               # outro pode ter preenchido entre o miss e a trava
                    if cached is not None:
                        self._count("hits")
                        return json.loads(cached)
                    self._count("misses")
                    value = self.loader(key)
                    self.redis.set(cache_key, json.dumps(value), ex=self.ttl)
                    return value
                finally:
                    self.redis.delete(lock_key)
            waited = True
            time.sleep(0.01)

    def invalidate(self, key):
        return bool(self.redis.delete(f"{self.prefix}:{key}"))
