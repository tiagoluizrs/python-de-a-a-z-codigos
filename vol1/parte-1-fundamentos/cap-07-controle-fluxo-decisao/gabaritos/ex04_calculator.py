"""Gabarito 4: calculadora sobre mini AST."""


def evaluate(node):
    match node:
        # bool é int: rejeitamos antes de aceitar números
        case bool():
            raise ValueError(f"invalid node: {node!r}")
        case int() | float():
            return node
        case ("+", a, b):
            return evaluate(a) + evaluate(b)
        case ("-", a, b):
            return evaluate(a) - evaluate(b)
        case ("*", a, b):
            return evaluate(a) * evaluate(b)
        case ("/", a, b):
            return evaluate(a) / evaluate(b)
        case ("neg", a):
            return -evaluate(a)
        case ("sum", [*nodes]):
            return sum(evaluate(n) for n in nodes)
        case _:
            raise ValueError(f"invalid node: {node!r}")
