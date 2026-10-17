"""Mede match, if/elif e despacho por dict (Python 3.15)."""
import operator
import sys
import timeit

OPS = {"add": operator.add, "sub": operator.sub,
       "mul": operator.mul, "div": operator.truediv}


def with_if(op, a, b):
    if op == "add":
        return a + b
    elif op == "sub":
        return a - b
    elif op == "mul":
        return a * b
    elif op == "div":
        return a / b


def with_match(op, a, b):
    match op:
        case "add":
            return a + b
        case "sub":
            return a - b
        case "mul":
            return a * b
        case "div":
            return a / b


def with_dict(op, a, b):
    return OPS[op](a, b)


def with_dict_lambda(op, a, b):
    return TABLE[op](a, b)


TABLE = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b,
         "mul": lambda a, b: a * b, "div": lambda a, b: a / b}

if __name__ == "__main__":
    print(sys.version)
    n = 1_000_000
    for op in ("add", "div"):
        print(f"ramo: {op}")
        for func in (with_if, with_match, with_dict, with_dict_lambda):
            best = min(timeit.repeat(
                lambda: func(op, 6, 3), number=n, repeat=5))
            print(f"  {func.__name__:16} {best / n * 1e9:6.1f} ns")
