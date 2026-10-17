"""Gabarito do exercício 3."""
import threading


class PerThread:
    def __init__(self, factory, close=None):
        self._factory, self._close = factory, close
        self._local = threading.local()
        self._resources = []
        self._lock = threading.Lock()
        self._generation = 0

    def get(self):
        entry = getattr(self._local, "entry", None)
        if entry is None or entry[0] != self._generation:
            resource = self._factory()
            with self._lock:
                self._resources.append(resource)
                entry = (self._generation, resource)
            self._local.entry = entry
        return entry[1]

    @property
    def count(self):
        with self._lock:
            return len(self._resources)

    def close_all(self):
        with self._lock:
            resources, self._resources = self._resources, []
            self._generation += 1
        first = None
        for resource in resources:
            try:
                if self._close:
                    self._close(resource)
            except BaseException as error:
                first = first or error
        if first:
            raise first
