"""Gabarito do exercício 3."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Add:
    left: object
    right: object


@dataclass(frozen=True)
class Mul:
    left: object
    right: object


@dataclass(frozen=True)
class Neg:
    operand: object


def _rewrite(node):
    match node:
        case Add(Num(0), x) | Add(x, Num(0)):
            return x
        case Mul(Num(1), x) | Mul(x, Num(1)):
            return x
        case Mul(Num(0), _) | Mul(_, Num(0)):
            return Num(0)
        case Neg(Neg(x)):
            return x
        case Neg(Num(n)):
            return Num(-n)
        case Add(Num(a), Num(b)):
            return Num(a + b)
        case Mul(Num(a), Num(b)):
            return Num(a * b)
    return node


def simplify(node):
    match node:
        case Add(left, right):
            node = Add(simplify(left), simplify(right))
        case Mul(left, right):
            node = Mul(simplify(left), simplify(right))
        case Neg(operand):
            node = Neg(simplify(operand))
    new = _rewrite(node)
    return node if new == node else simplify(new)


def derive(node, var):
    match node:
        case Num(_):
            result = Num(0)
        case Var(name):
            result = Num(1) if name == var else Num(0)
        case Add(a, b):
            result = Add(derive(a, var), derive(b, var))
        case Mul(a, b):
            result = Add(Mul(derive(a, var), b), Mul(a, derive(b, var)))
        case Neg(a):
            result = Neg(derive(a, var))
        case _:
            raise TypeError(f"nó desconhecido: {type(node).__name__}")
    return simplify(result)


def substitute(node, env):
    match node:
        case Var(name) if name in env:
            return Num(env[name])
        case Add(a, b):
            return Add(substitute(a, env), substitute(b, env))
        case Mul(a, b):
            return Mul(substitute(a, env), substitute(b, env))
        case Neg(a):
            return Neg(substitute(a, env))
        case _:
            return node
