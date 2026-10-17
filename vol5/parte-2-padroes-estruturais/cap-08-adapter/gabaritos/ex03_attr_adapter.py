"""Gabarito do exercício 3."""


class Renamed:
    def __init__(self, obj, mapping):
        for old in mapping.values():
            if not hasattr(obj, old):
                raise ValueError(f"atributo inexistente: {old}")
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_mapping", dict(mapping))

    def _real(self, name):
        return self._mapping.get(name, name)

    def __getattr__(self, name):
        return getattr(self._obj, self._real(name))

    def __setattr__(self, name, value):
        setattr(self._obj, self._real(name), value)

    def __delattr__(self, name):
        delattr(self._obj, self._real(name))

    def __dir__(self):
        reverse = {old: new for new, old in self._mapping.items()}
        return sorted({reverse.get(name, name) for name in dir(self._obj)})

    def __repr__(self):
        return f"Renamed({self._obj!r})"

    def unwrap(self):
        return self._obj
