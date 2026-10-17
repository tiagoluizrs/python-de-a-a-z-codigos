"""Gabarito do exercício 3."""
import threading


class IdempotentExecutor:
    def __init__(self, clock, ttl=None):
        self.clock, self.ttl = clock, ttl
        self._results: dict = {}
        self._locks: dict = {}
        self._guard = threading.Lock()
        self._stats = {"executed": 0, "replayed": 0, "failed": 0}

    def _lock_for(self, key):
        with self._guard:
            return self._locks.setdefault(key, threading.Lock())

    def run(self, key, fn):
        lock = self._lock_for(key)
        with lock:
            entry = self._results.get(key)
            if entry is not None and (self.ttl is None or self.clock() - entry[1] < self.ttl):
                with self._guard:
                    self._stats["replayed"] += 1
                return entry[0]
            try:
                result = fn()
            except Exception:
                with self._guard:
                    self._stats["failed"] += 1
                raise
            self._results[key] = (result, self.clock())
            with self._guard:
                self._stats["executed"] += 1
            return result

    @property
    def stats(self):
        with self._guard:
            return dict(self._stats)


def make_key(task_name, **params):
    parts = [f"{k}={v}" for k, v in sorted(params.items()) if v is not None]
    return "|".join([task_name, *parts])
