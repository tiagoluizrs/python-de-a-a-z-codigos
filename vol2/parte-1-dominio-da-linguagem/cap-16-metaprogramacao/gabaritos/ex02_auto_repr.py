"""Gabarito do exercício 2."""
import inspect


def auto_repr(cls):
    if "__repr__" in vars(cls):
        return cls
    params = [p.name for p in inspect.signature(cls.__init__).parameters.values()
              if p.name != "self" and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]

    def __repr__(self):
        body = ", ".join(f"{name}={getattr(self, name)!r}" for name in params)
        return f"{type(self).__name__}({body})"

    cls.__repr__ = __repr__
    return cls
