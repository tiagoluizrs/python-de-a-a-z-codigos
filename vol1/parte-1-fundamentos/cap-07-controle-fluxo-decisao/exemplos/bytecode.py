"""Bytecode de match simples versus if/elif."""
import dis


def with_match(x):
    match x:
        case 1:
            return "one"
        case 2:
            return "two"
        case _:
            return "other"


def with_if(x):
    if x == 1:
        return "one"
    elif x == 2:
        return "two"
    else:
        return "other"


print("--- match")
dis.dis(with_match)
print("--- if/elif")
dis.dis(with_if)


def structural(cmd):
    match cmd:
        case [a, b]:
            return a
        case {"k": v}:
            return v
        case int():
            return 0


print("--- padroes estruturais: so os opcodes de match")
names = {i.opname for i in dis.get_instructions(structural)}
print(sorted(n for n in names if "MATCH" in n or n in
             ("GET_LEN", "UNPACK_SEQUENCE", "BINARY_OP", "CALL")
             or n.startswith("GET_") or n == "COPY"))
