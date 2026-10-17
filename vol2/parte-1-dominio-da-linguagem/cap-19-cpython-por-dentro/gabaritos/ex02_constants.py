"""Gabarito do exercício 2."""
import dis
import types


def _walk(code):
    yield code
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from _walk(const)


def constants_of(source):
    found = set()
    for code in _walk(compile(source, "<src>", "exec")):
        for const in code.co_consts:
            if type(const) in (int, float, str):
                found.add(const)
    return sorted(found, key=repr)


def is_folded(expression):
    code = compile(expression, "<expr>", "eval")
    return not any(i.opname in ("BINARY_OP", "CALL") for i in dis.get_instructions(code))
