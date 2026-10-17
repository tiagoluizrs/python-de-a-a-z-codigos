"""Gabarito do exercício 1."""
import sys


def deep_size(obj, _seen: set[int] | None = None) -> int:
    seen = set() if _seen is None else _seen
    if id(obj) in seen:           # já contado (compartilhado ou circular)
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        for key, value in obj.items():
            size += deep_size(key, seen) + deep_size(value, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            size += deep_size(item, seen)
    return size
