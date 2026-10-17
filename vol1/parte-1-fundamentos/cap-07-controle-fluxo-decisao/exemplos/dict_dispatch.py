"""Despacho por dicionário: tabela de comandos."""
import operator

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def calc(a, op, b):
    try:
        func = OPS[op]
    except KeyError:
        raise ValueError(f"unknown operator: {op!r}") from None
    return func(a, b)


print(calc(6, "*", 7))
try:
    calc(1, "^", 2)
except ValueError as exc:
    print(exc)

# Ação com argumentos: funções como valores
def greet(name): return f"hello, {name}"
def bye(name): return f"bye, {name}"


COMMANDS = {"greet": greet, "bye": bye}
print(COMMANDS.get("greet", bye)("Ana"))

# Cuidado: valores do dict são avaliados ao construir o dict
def expensive():
    print("expensive() chamada")
    return 1


table = {"a": expensive(), "b": expensive()}   # chama as duas!
lazy = {"a": expensive, "b": expensive}        # só referências
print(lazy["a"]())
