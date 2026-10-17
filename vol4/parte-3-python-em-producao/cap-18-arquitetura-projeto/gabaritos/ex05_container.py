"""Gabarito do exercício 5."""
from contextlib import contextmanager


class DependencyError(Exception):
    pass


class Container:
    def __init__(self):
        self._factories = {}
        self._cache = {}
        self._overrides = {}
        self._building = []
        self._built = set()

    def register(self, name, factory, singleton=True):
        if name in self._factories:
            raise DependencyError(f"já registrado: {name}")
        self._factories[name] = (factory, singleton)

    def get(self, name):
        if name in self._overrides:
            return self._overrides[name]
        if name not in self._factories:
            raise DependencyError(f"desconhecido: {name}")
        if name in self._cache:
            return self._cache[name]
        if name in self._building:
            cycle = self._building[self._building.index(name):] + [name]
            raise DependencyError("ciclo: " + " -> ".join(cycle))
        factory, singleton = self._factories[name]
        self._building.append(name)
        try:
            instance = factory(self)
        finally:
            self._building.pop()
        self._built.add(name)
        if singleton:
            self._cache[name] = instance
        return instance

    @contextmanager
    def override(self, name, value):
        if name not in self._factories:
            raise DependencyError(f"desconhecido: {name}")
        missing = object()
        previous = self._overrides.get(name, missing)
        self._overrides[name] = value
        try:
            yield
        finally:
            if previous is missing:
                del self._overrides[name]
            else:
                self._overrides[name] = previous

    @property
    def built(self):
        return set(self._built)
