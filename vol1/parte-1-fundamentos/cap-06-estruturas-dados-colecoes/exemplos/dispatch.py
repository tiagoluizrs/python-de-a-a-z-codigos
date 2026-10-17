"""Dict como tabela de despacho no lugar de if/elif."""
import operator


def apply_if(op, a, b):
    if op == "add":
        return a + b
    elif op == "sub":
        return a - b
    elif op == "mul":
        return a * b
    raise ValueError(f"unknown operation: {op}")


OPS = {"add": operator.add, "sub": operator.sub, "mul": operator.mul}


def apply_dict(op, a, b):
    try:
        func = OPS[op]
    except KeyError:
        raise ValueError(f"unknown operation: {op}") from None
    return func(a, b)


print(apply_if("mul", 3, 4), apply_dict("mul", 3, 4))
OPS["pow"] = operator.pow          # extensível em tempo de execução
print(apply_dict("pow", 2, 10))
try:
    apply_dict("div", 1, 2)
except ValueError as error:
    print(error)
