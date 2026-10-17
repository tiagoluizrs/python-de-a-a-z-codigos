"""Gabarito do exercício 3."""
from functools import singledispatch


@singledispatch
def describe(value):
    return f"<{type(value).__name__}>"


@describe.register(bool)
def _(value):
    return "yes" if value else "no"


@describe.register(int)
def _(value):
    return f"int({value})"


@describe.register(float)
def _(value):
    return f"float({value:.1f})"


@describe.register(str)
def _(value):
    return f"'{value}'"


@describe.register(type(None))
def _(value):
    return "nothing"


@describe.register(list)
@describe.register(tuple)
def _(value):
    return "[" + ", ".join(describe(v) for v in value) + "]"


@describe.register(set)
def _(value):
    return "[" + ", ".join(sorted(describe(v) for v in value)) + "]"


@describe.register(dict)
def _(value):
    return "{" + ", ".join(f"{describe(k)}: {describe(v)}" for k, v in value.items()) + "}"
