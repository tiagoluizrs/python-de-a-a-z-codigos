"""Gabarito do exercício 1."""
import threading
from contextlib import contextmanager


class Registry:
    def __init__(self, kind="plugin"):
        self.kind = kind
        self._items = {}
        self._lock = threading.RLock()
        self._frozen = False

    @staticmethod
    def _key(name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("nome inválido")
        return name.strip().lower()

    def _check_open(self):
        if self._frozen:
            raise RuntimeError("registro congelado")

    def add(self, name, obj, *, replace=False):
        key = self._key(name)
        with self._lock:
            self._check_open()
            if key in self._items and not replace:
                raise ValueError(f"{self.kind} já registrado: {key}")
            self._items[key] = obj
        return obj

    def register(self, name=None, *, replace=False):
        if name is not None and not isinstance(name, str) and callable(name):          # @reg.register, sem parênteses
            return self.add(name.__name__, name)

        def decorator(obj):
            return self.add(name if name is not None else obj.__name__, obj, replace=replace)

        return decorator

    def get(self, name):
        with self._lock:
            try:
                return self._items[self._key(name)]
            except (KeyError, ValueError):
                available = ", ".join(sorted(self._items)) or "nenhum"
                raise KeyError(f"{self.kind} desconhecido: {name!r}; disponíveis: {available}") from None

    def create(self, name, *args, **kwargs):
        return self.get(name)(*args, **kwargs)

    def __contains__(self, name):
        try:
            return self._key(name) in self._items
        except ValueError:
            return False

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self.names())

    def names(self):
        with self._lock:
            return sorted(self._items)

    def items(self):
        with self._lock:
            return sorted(self._items.items())

    def unregister(self, name):
        with self._lock:
            self._check_open()
            obj = self.get(name)
            del self._items[self._key(name)]
            return obj

    def snapshot(self):
        with self._lock:
            return dict(self._items)

    def restore(self, snapshot):
        with self._lock:
            self._check_open()
            self._items = dict(snapshot)

    @contextmanager
    def isolated(self):
        with self._lock:
            self._check_open()
            saved = dict(self._items)
        try:
            yield self
        finally:
            with self._lock:
                self._items = saved

    def freeze(self):
        with self._lock:
            self._frozen = True
        return self

    @property
    def frozen(self):
        return self._frozen
