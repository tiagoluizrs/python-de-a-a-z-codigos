"""Gabarito do exercício 3."""
import sys
from collections import deque


def deep_size(obj, _seen=None):
    seen = set() if _seen is None else _seen
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset, deque)):
        size += sum(deep_size(item, seen) for item in obj)
    elif not isinstance(obj, (str, bytes, bytearray, int, float, complex, bool, type(None))):
        if hasattr(obj, "__dict__"):
            size += deep_size(obj.__dict__, seen)
        for cls in type(obj).__mro__:
            slots = cls.__dict__.get("__slots__", ())
            for name in ((slots,) if isinstance(slots, str) else slots):
                try:
                    size += deep_size(getattr(obj, name), seen)
                except AttributeError:
                    pass
    return size


def per_object(factories, n):
    if n < 1:
        raise ValueError("n deve ser >= 1")
    return {name: round(deep_size([factory(i) for i in range(n)]) / n, 1) for name, factory in factories.items()}


def savings_ratio(before, after):
    if after <= 0:
        raise ValueError("after deve ser positivo")
    return round(before / after, 2)


def shared_fraction(objects):
    if not objects:
        return 0.0
    return round(1 - len({id(o) for o in objects}) / len(objects), 3)
