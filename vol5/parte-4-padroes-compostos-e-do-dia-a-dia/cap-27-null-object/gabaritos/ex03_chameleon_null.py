"""Gabarito do exercício 3."""
from collections.abc import Mapping


class Null:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        return self

    def __setattr__(self, name, value):
        raise AttributeError("Null é imutável")

    def __delattr__(self, name):
        raise AttributeError("Null é imutável")

    def __call__(self, *args, **kwargs):
        return self

    def __getitem__(self, key):
        return self

    def __contains__(self, item):
        return False

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return False

    def __str__(self):
        return ""

    def __repr__(self):
        return "Null"

    def __eq__(self, other):
        return other is None or isinstance(other, Null)

    def __hash__(self):
        return hash(None)

    def _absorb(self, other):
        return self

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __truediv__ = __rtruediv__ = _absorb

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


NULL = Null()


def is_null(value):
    return value is NULL


def dig(obj, path, default=None):
    if path == "":
        return obj
    for step in path.split("."):
        try:
            obj = obj[step] if isinstance(obj, Mapping) else getattr(obj, step)
        except (KeyError, AttributeError):
            return default
    return obj
