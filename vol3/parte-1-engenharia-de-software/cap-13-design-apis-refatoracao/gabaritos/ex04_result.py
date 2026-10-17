"""Gabarito do exercício 4."""


class Ok:
    __slots__ = ("value",)

    def __init__(self, value):
        object.__setattr__(self, "value", value)

    def __setattr__(self, name, value):
        raise AttributeError("imutável")

    is_ok = property(lambda self: True)
    is_err = property(lambda self: False)

    def unwrap(self):
        return self.value

    def unwrap_or(self, default):
        return self.value

    def map(self, f):
        return Ok(f(self.value))

    def and_then(self, f):
        return f(self.value)

    def map_err(self, f):
        return self

    def __eq__(self, other):
        return isinstance(other, Ok) and self.value == other.value

    __hash__ = None

    def __repr__(self):
        return f"Ok({self.value!r})"


class Err:
    __slots__ = ("error",)

    def __init__(self, error):
        object.__setattr__(self, "error", error)

    def __setattr__(self, name, value):
        raise AttributeError("imutável")

    is_ok = property(lambda self: False)
    is_err = property(lambda self: True)

    def unwrap(self):
        raise RuntimeError(f"unwrap em Err: {self.error!r}")

    def unwrap_or(self, default):
        return default

    def map(self, f):
        return self

    def and_then(self, f):
        return self

    def map_err(self, f):
        return Err(f(self.error))

    def __eq__(self, other):
        return isinstance(other, Err) and self.error == other.error

    __hash__ = None

    def __repr__(self):
        return f"Err({self.error!r})"


def try_call(func, *args, catch=(Exception,), **kwargs):
    try:
        return Ok(func(*args, **kwargs))
    except catch as error:
        return Err(error)


def collect(results):
    values = []
    for result in results:
        if result.is_err:
            return result
        values.append(result.unwrap())
    return Ok(values)
