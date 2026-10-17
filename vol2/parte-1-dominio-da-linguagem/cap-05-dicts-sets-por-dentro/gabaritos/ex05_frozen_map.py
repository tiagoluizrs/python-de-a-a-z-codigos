"""Gabarito do exercício 5."""
from collections.abc import Mapping


class FrozenMap(Mapping):
    def __init__(self, data=()):
        self._data = dict(data)               # cópia: não guarda o dict do chamador

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __hash__(self):
        # frozenset ignora a ordem; os itens precisam ser hasheáveis
        return hash(frozenset(self._data.items()))
