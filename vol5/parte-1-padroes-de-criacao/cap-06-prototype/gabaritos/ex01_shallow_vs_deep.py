"""Gabarito do exercício 1."""

_MUTABLE = (dict, list, set)


def shared_mutables(a, b, _path=""):
    found = []
    if isinstance(a, _MUTABLE) and a is b:
        return [_path or "."]
    if isinstance(a, dict) and isinstance(b, dict):
        for key in a.keys() & b.keys():
            child = f"{_path}.{key}" if _path else str(key)
            found += shared_mutables(a[key], b[key], child)
    elif isinstance(a, (list, tuple)) and type(a) is type(b):
        for i in range(min(len(a), len(b))):
            found += shared_mutables(a[i], b[i], f"{_path}[{i}]")
    return sorted(found)


def is_independent(a, b):
    return not shared_mutables(a, b)


def make_grid(rows, cols, value=0):
    if rows < 0 or cols < 0:
        raise ValueError("dimensões negativas")
    return [[value] * cols for _ in range(rows)]
