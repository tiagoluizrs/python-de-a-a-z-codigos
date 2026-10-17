"""Gabarito do exercício 1."""
import threading

_MISSING = object()


class LazyProxy:
    def __init__(self, factory):
        object.__setattr__(self, "_factory", factory)
        object.__setattr__(self, "_target", _MISSING)
        object.__setattr__(self, "_lock", threading.Lock())

    def _load(self):
        if self._target is _MISSING:
            with self._lock:
                if self._target is _MISSING:
                    object.__setattr__(self, "_target", self._factory())
        return self._target

    def __getattr__(self, name):
        return getattr(self._load(), name)

    def __setattr__(self, name, value):
        setattr(self._load(), name, value)

    def __delattr__(self, name):
        delattr(self._load(), name)

    def __len__(self):
        return len(self._load())

    def __iter__(self):
        return iter(self._load())

    def __getitem__(self, key):
        return self._load()[key]

    def __setitem__(self, key, value):
        self._load()[key] = value

    def __delitem__(self, key):
        del self._load()[key]

    def __contains__(self, item):
        return item in self._load()

    def __bool__(self):
        return bool(self._load())

    def __str__(self):
        return str(self._load())

    def __repr__(self):
        if self._target is _MISSING:
            return "<LazyProxy não carregado>"
        return f"<LazyProxy {self._target!r}>"

    def __eq__(self, other):
        if isinstance(other, LazyProxy):
            other = other.unwrap()
        return self._load() == other

    def __hash__(self):
        return hash(self._load())

    def __call__(self, *args, **kwargs):
        return self._load()(*args, **kwargs)

    def __enter__(self):
        return self._load().__enter__()

    def __exit__(self, *exc):
        return self._load().__exit__(*exc)

    @property
    def __class__(self):
        return type(self._load())

    @property
    def is_loaded(self):
        return self._target is not _MISSING

    def unwrap(self):
        return self._load()

    def reset(self):
        object.__setattr__(self, "_target", _MISSING)
