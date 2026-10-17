"""Gabarito do exercício 4."""


class lazy:
    def __init__(self, fn):
        self.fn, self.name = fn, fn.__name__
        self.__doc__ = fn.__doc__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        value = self.fn(obj)
        obj.__dict__[self.name] = value
        return value


def reset_lazy(instance, name):
    return instance.__dict__.pop(name, _MISSING) is not _MISSING


_MISSING = object()


class Bounded:
    def __init__(self, minimum=None, maximum=None, kind=(int, float)):
        self.minimum, self.maximum, self.kind = minimum, maximum, kind
        self.name = "?"

    def __set_name__(self, owner, name):
        self.name = name

    @property
    def _slot(self):
        return "_" + self.name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self._slot]
        except KeyError:
            raise AttributeError(f"{self.name} não foi definido") from None

    def __set__(self, obj, value):
        if isinstance(value, bool) or not isinstance(value, self.kind):
            raise TypeError(f"{self.name} deve ser numérico")
        if (self.minimum is not None and value < self.minimum) or (self.maximum is not None and value > self.maximum):
            raise ValueError(f"{self.name} fora do intervalo [{self.minimum}, {self.maximum}]")
        obj.__dict__[self._slot] = value

    def __delete__(self, obj):
        raise AttributeError(f"{self.name} não pode ser apagado")
