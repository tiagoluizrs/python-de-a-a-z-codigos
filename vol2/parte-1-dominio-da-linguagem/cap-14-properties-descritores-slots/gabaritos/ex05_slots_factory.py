"""Gabarito do exercício 5."""


def make_record(name, fields, weakref=False):
    fields = tuple(fields)
    slots = fields + (("__weakref__",) if weakref else ())

    def __init__(self, *args, **kwargs):
        if len(args) > len(fields):
            raise TypeError("argumentos demais")
        values = dict(zip(fields, args))
        for key, value in kwargs.items():
            if key not in fields or key in values:
                raise TypeError(f"argumento inválido: {key!r}")
            values[key] = value
        missing = [f for f in fields if f not in values]
        if missing:
            raise TypeError(f"faltam campos: {missing}")
        for key, value in values.items():
            setattr(self, key, value)

    def __repr__(self):
        body = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
        return f"{type(self).__name__}({body})"

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return all(getattr(self, f) == getattr(other, f) for f in fields)

    namespace = {"__slots__": slots, "__init__": __init__, "__repr__": __repr__,
                 "__eq__": __eq__, "__hash__": None}
    return type(name, (), namespace)
