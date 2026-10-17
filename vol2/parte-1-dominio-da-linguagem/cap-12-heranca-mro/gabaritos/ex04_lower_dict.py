"""Gabarito do exercício 4."""
from collections import UserDict


class LowerDict(UserDict):
    @staticmethod
    def _norm(key):
        return key.lower() if isinstance(key, str) else key

    def __setitem__(self, key, value):
        super().__setitem__(self._norm(key), value)

    def __getitem__(self, key):
        return super().__getitem__(self._norm(key))

    def __delitem__(self, key):
        super().__delitem__(self._norm(key))

    def __contains__(self, key):
        return super().__contains__(self._norm(key))
