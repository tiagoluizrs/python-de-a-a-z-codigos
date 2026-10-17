"""Gabarito do exercício 4."""
from collections import ChainMap


class LayeredConfig:
    def __init__(self, **layers):
        if not layers:
            raise ValueError("sem camadas")
        self._names = list(layers)
        self._maps = [dict(layer) for layer in layers.values()]
        self._chain = ChainMap(*self._maps)

    def __getitem__(self, key):
        return self._chain[key]

    def get(self, key, default=None):
        return self._chain.get(key, default)

    def __setitem__(self, key, value):
        self._maps[0][key] = value

    def __contains__(self, key):
        return key in self._chain

    def __len__(self):
        return len(self._chain)

    def __iter__(self):
        return iter(self._chain)

    def source(self, key):
        for name, layer in zip(self._names, self._maps):
            if key in layer:
                return name
        raise KeyError(key)

    @property
    def layers(self):
        return list(self._names)

    def _copy(self, names, maps):
        return LayeredConfig(**dict(zip(names, maps)))

    def override(self, **values):
        return self._copy(["override"] + self._names, [dict(values)] + self._maps)

    def without(self, key):
        return self._copy(self._names, [{k: v for k, v in layer.items() if k != key} for layer in self._maps])

    def flatten(self):
        return dict(self._chain)

    def shadowed(self, key):
        return [(name, layer[key]) for name, layer in zip(self._names, self._maps) if key in layer]
