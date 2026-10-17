"""Exercício 4: dispatcher por tipo com singledispatch (gabarito)."""
import functools


@functools.singledispatch
def describe(value):
    return f"object:{type(value).__name__}"


@describe.register
def _(value: bool):
    # bool é mais específico que int: o despacho escolhe esta
    return f"bool:{value}"


@describe.register
def _(value: int):
    return f"int:{value}"


@describe.register
def _(value: str):
    return f"str:{len(value)}"


@describe.register(list)
@describe.register(tuple)
def _(value):
    return "seq[" + ",".join(describe(v) for v in value) + "]"


@describe.register
def _(value: dict):
    return f"map:{len(value)}"


@describe.register(type(None))
def _(value):
    return "none"
