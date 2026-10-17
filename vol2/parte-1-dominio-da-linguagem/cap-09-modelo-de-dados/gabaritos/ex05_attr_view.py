"""Gabarito do exercício 5."""


class AttrView:
    def __init__(self, data):
        object.__setattr__(self, "_data", dict(data))     # contorna o __setattr__

    def __getattr__(self, name):
        # só é chamado quando a busca normal falha
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}") from None

    def __setattr__(self, name, value):
        raise AttributeError("AttrView é somente leitura")

    def __delattr__(self, name):
        raise AttributeError("AttrView é somente leitura")

    def __dir__(self):
        return sorted(self._data)
