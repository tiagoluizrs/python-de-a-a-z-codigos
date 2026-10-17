"""Gabarito do exercício 3."""
from collections.abc import MutableMapping


class LimitedDict(MutableMapping):
    def __init__(self, max_items=3, validator=None, initial=None):
        if max_items < 1:
            raise ValueError("max_items deve ser >= 1")
        self.max_items, self.validator = max_items, validator
        self._data: dict = {}
        if initial is not None:
            self.update(initial)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if self.validator is not None and not self.validator(value):
            raise ValueError(f"valor inválido: {value!r}")
        if key not in self._data and len(self._data) >= self.max_items:
            raise OverflowError("dicionário cheio")
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def copy(self):
        clone = LimitedDict(self.max_items, self.validator)
        clone._data = dict(self._data)
        return clone
