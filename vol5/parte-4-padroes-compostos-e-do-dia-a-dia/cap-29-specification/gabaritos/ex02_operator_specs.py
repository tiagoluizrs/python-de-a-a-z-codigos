"""Gabarito do exercício 2."""
from collections.abc import Mapping


def _wrap(other):
    if isinstance(other, Spec):
        return other
    if callable(other):
        return Spec(other, getattr(other, "__name__", "?"))
    return None


class Spec:
    def __init__(self, fn, description="?"):
        if not callable(fn):
            raise TypeError("fn precisa ser chamável")
        self.fn, self.description = fn, description

    def __call__(self, item):
        return bool(self.fn(item))

    def __and__(self, other):
        other = _wrap(other)
        if other is None:
            return NotImplemented
        return Spec(lambda item: self(item) and other(item), f"({self.description} e {other.description})")

    def __rand__(self, other):
        other = _wrap(other)
        if other is None:
            return NotImplemented
        return other & self

    def __or__(self, other):
        other = _wrap(other)
        if other is None:
            return NotImplemented
        return Spec(lambda item: self(item) or other(item), f"({self.description} ou {other.description})")

    def __ror__(self, other):
        other = _wrap(other)
        if other is None:
            return NotImplemented
        return other | self

    def __invert__(self):
        return Spec(lambda item: not self(item), f"não {self.description}")

    def __repr__(self):
        return self.description


def spec(description):
    return lambda fn: Spec(fn, description)


def all_of(*specs):
    if not specs:
        return Spec(lambda item: True, "sempre")
    result = _wrap(specs[0])
    for other in specs[1:]:
        result = result & other
    return result


def any_of(*specs):
    if not specs:
        return Spec(lambda item: False, "nunca")
    result = _wrap(specs[0])
    for other in specs[1:]:
        result = result | other
    return result


_MISSING = object()


def _field(item, name):
    if isinstance(item, Mapping):
        return item.get(name, _MISSING)
    return getattr(item, name, _MISSING)


def where(**conditions):
    if not conditions:
        return Spec(lambda item: True, "sempre")
    pairs = list(conditions.items())

    def matches(item):
        for name, expected in pairs:
            actual = _field(item, name)
            if actual is _MISSING or actual != expected:
                return False
        return True

    return Spec(matches, " e ".join(f"{name} == {expected!r}" for name, expected in pairs))


def filter_by(rule, items):
    return [item for item in items if rule(item)]
