"""Gabarito do exercício 3."""
import copy


class PrototypeRegistry:
    def __init__(self):
        self._items = {}

    def register(self, name, prototype):
        if not name:
            raise ValueError("nome vazio")
        if name in self._items:
            raise ValueError(f"protótipo já registrado: {name}")
        self._items[name] = copy.deepcopy(prototype)

    def create(self, name, **changes):
        if name not in self._items:
            available = ", ".join(sorted(self._items)) or "nenhum"
            raise KeyError(f"protótipo desconhecido: {name}; disponíveis: {available}")
        stored = self._items[name]
        for attribute in changes:
            if not hasattr(stored, attribute):
                raise AttributeError(f"{attribute!r} não é um atributo de {type(stored).__name__}")
        clone = copy.deepcopy(stored)
        for attribute, value in changes.items():
            setattr(clone, attribute, value)
        return clone

    def names(self):
        return sorted(self._items)

    def unregister(self, name):
        del self._items[name]

    def __len__(self):
        return len(self._items)

    def __contains__(self, name):
        return name in self._items
