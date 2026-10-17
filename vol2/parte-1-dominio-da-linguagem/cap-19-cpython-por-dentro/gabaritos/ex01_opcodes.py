"""Gabarito do exercício 1."""
import dis
import types
from collections import Counter


def _code_objects(code):
    yield code
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from _code_objects(const)


def _instructions(func):
    for code in _code_objects(func.__code__):
        yield from dis.get_instructions(code)


def opcode_histogram(func):
    return Counter(i.opname for i in _instructions(func))


def count_instructions(func):
    return sum(1 for _ in _instructions(func))


def uses_global(func, name):
    return any(i.opname == "LOAD_GLOBAL" and i.argval == name for i in _instructions(func))
