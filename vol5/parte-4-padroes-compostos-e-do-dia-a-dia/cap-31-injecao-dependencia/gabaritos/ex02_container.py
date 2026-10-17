"""Gabarito do exercício 2."""
import functools
import inspect
from contextlib import contextmanager
from typing import get_type_hints


@functools.cache
def _plan(factory):
    hints = get_type_hints(factory.__init__ if isinstance(factory, type) else factory)
    return tuple((name, hints.get(name), param.default is not inspect.Parameter.empty) for name, param in inspect.signature(factory).parameters.items())


def _name(key):
    return getattr(key, "__name__", str(key))


class Container:
    def __init__(self):
        self._providers, self._singletons, self._overrides = {}, {}, {}

    def register(self, key, factory=None, *, lifetime="singleton"):
        if lifetime not in ("singleton", "transient"):
            raise ValueError(f"lifetime inválido: {lifetime}")
        self._providers[key] = (factory or key, lifetime)
        self._singletons.pop(key, None)

    def register_instance(self, key, obj):
        self._providers[key] = (lambda: obj, "singleton")
        self._singletons[key] = obj
        return obj

    def has(self, key):
        return key in self._providers or key in self._overrides

    def resolve(self, key, _chain=()):
        if key in self._overrides:
            return self._overrides[key]
        if key in _chain:
            raise RuntimeError("dependência circular: " + " -> ".join(_name(k) for k in (*_chain, key)))
        if key not in self._providers:
            suffix = f" (cadeia: {' -> '.join(_name(k) for k in (*_chain, key))})" if _chain else ""
            raise LookupError(f"não registrado: {_name(key)}{suffix}")
        factory, lifetime = self._providers[key]
        if lifetime == "singleton" and key in self._singletons:
            return self._singletons[key]
        kwargs = {}
        for name, hint, has_default in _plan(factory):
            if hint is not None and self.has(hint):
                kwargs[name] = self.resolve(hint, (*_chain, key))
            elif has_default:
                continue
            elif hint is not None:
                raise LookupError(f"não registrado: {_name(hint)} (cadeia: {' -> '.join(_name(k) for k in (*_chain, key, hint))})")
            else:
                raise TypeError(f"parâmetro sem tipo: {_name(key)}.{name}")
        instance = factory(**kwargs)
        if lifetime == "singleton":
            self._singletons[key] = instance
        return instance

    @contextmanager
    def override(self, key, instance):
        self._overrides[key] = instance
        self._singletons.clear()
        try:
            yield instance
        finally:
            del self._overrides[key]
            self._singletons.clear()
