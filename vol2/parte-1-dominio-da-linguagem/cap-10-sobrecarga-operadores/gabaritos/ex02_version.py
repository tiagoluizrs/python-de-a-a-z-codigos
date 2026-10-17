"""Gabarito do exercício 2."""
import functools


@functools.total_ordering
class Version:
    def __init__(self, text):
        self.text = text
        parts = [int(p) for p in text.split(".")]
        self.parts = tuple(parts + [0] * (3 - len(parts)))   # "2" vira (2, 0, 0)

    def __repr__(self):
        return f"Version({self.text!r})"

    @staticmethod
    def _coerce(other):
        if isinstance(other, Version):
            return other
        if isinstance(other, str):
            return Version(other)
        return None

    def __eq__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self.parts < other.parts

    def __hash__(self):
        return hash(self.parts)
