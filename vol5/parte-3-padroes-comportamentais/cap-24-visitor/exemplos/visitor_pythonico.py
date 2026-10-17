"""Visitor em Python: functools.singledispatch, match/case, ast.NodeVisitor e a pilha explícita (sem o accept/visit)."""
import ast
import time
from dataclasses import dataclass
from functools import singledispatch
from typing import assert_never


# --- 1. os nós: dados puros, sem accept e sem operações ---
@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Add:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Mul:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Neg:
    operand: "Expr"


Expr = Num | Var | Add | Mul | Neg


# --- 2. singledispatch: uma função por tipo, registradas FORA das classes ---
@singledispatch
def evaluate(node, env):
    raise TypeError(f"nó desconhecido: {type(node).__name__}")


@evaluate.register
def _(node: Num, env):
    return node.value


@evaluate.register
def _(node: Var, env):
    return env[node.name]


@evaluate.register
def _(node: Add, env):
    return evaluate(node.left, env) + evaluate(node.right, env)


@evaluate.register
def _(node: Mul, env):
    return evaluate(node.left, env) * evaluate(node.right, env)


@evaluate.register
def _(node: Neg, env):
    return -evaluate(node.operand, env)


expr = Add(Num(2), Mul(Var("x"), Neg(Num(5))))
print("singledispatch:", evaluate(expr, {"x": 4}), "| tipos registrados:", sorted(t.__name__ for t in evaluate.registry if t is not object))


@dataclass(frozen=True)
class Pow:                                                  # um tipo NOVO, definido DEPOIS (poderia vir de outra biblioteca)
    base: "Expr"
    exponent: "Expr"


@evaluate.register
def _(node: Pow, env):                                       # ...e a operação é estendida sem editar nenhuma outra função
    return evaluate(node.base, env) ** evaluate(node.exponent, env)


print("um tipo novo estende a operação de fora:", evaluate(Pow(Num(2), Num(10)), {}))
try:
    evaluate("não é um nó", {})
except TypeError as error:
    print("fora do registro:", error)


# --- 3. match/case: o padrão estrutural resolve o Visitor e ainda enxerga DENTRO dos nós ---
def show(node):
    match node:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Add(left, right):
            return f"({show(left)} + {show(right)})"
        case Mul(left, right):
            return f"{show(left)} * {show(right)}"
        case Neg(operand):
            return f"-{show(operand)}"
        case _:
            assert_never(node)                              # o verificador de tipos avisa se um tipo do Expr ficou de fora


def simplify(node):
    """Reescreve a árvore: padrões ANINHADOS (0 + x, 1 * x, --x), o que um Visitor clássico faria com um monte de ifs."""
    match node:
        case Add(Num(0), x) | Add(x, Num(0)):
            return simplify(x)
        case Mul(Num(1), x) | Mul(x, Num(1)):
            return simplify(x)
        case Mul(Num(0), _) | Mul(_, Num(0)):
            return Num(0)
        case Neg(Neg(x)):
            return simplify(x)
        case Add(Num(a), Num(b)):
            return Num(a + b)
        case Mul(Num(a), Num(b)):
            return Num(a * b)
        case Add(left, right):
            new = Add(simplify(left), simplify(right))
            return simplify(new) if new != node else node
        case Mul(left, right):
            new = Mul(simplify(left), simplify(right))
            return simplify(new) if new != node else node
        case Neg(x):
            return Neg(simplify(x))
        case _:
            return node


messy = Add(Mul(Num(1), Var("x")), Mul(Num(0), Add(Var("y"), Num(9))))
print("\nmatch:", show(expr), "| simplificar", show(messy), "->", show(simplify(messy)))
print("-(-(x + 0)) ->", show(simplify(Neg(Neg(Add(Var("x"), Num(0)))))), "| 2 + 3 * 4 ->", show(simplify(Add(Num(2), Mul(Num(3), Num(4))))))


# --- 4. a biblioteca padrão: ast.NodeVisitor e ast.NodeTransformer ---
SOURCE = """
import os
from collections import deque

def area(w, h):
    return w * h

def report(items):
    for item in items:
        print(area(item.w, item.h) + 2 * 3)
"""


class Inspector(ast.NodeVisitor):
    def __init__(self):
        self.functions, self.calls = [], []

    def visit_FunctionDef(self, node):                      # o NOME do método escolhe o tipo: visit_<NomeDaClasse>
        self.functions.append(node.name)
        self.generic_visit(node)                            # continua descendo pelos filhos

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        self.generic_visit(node)


inspector = Inspector()
inspector.visit(ast.parse(SOURCE))
print("\nast.NodeVisitor:", "funções", inspector.functions, "| chamadas", inspector.calls)


class Fold(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)                            # primeiro os filhos (de baixo para cima)
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant) and isinstance(node.op, ast.Mult):
            return ast.copy_location(ast.Constant(node.left.value * node.right.value), node)
        return node


folded = ast.unparse(Fold().visit(ast.parse(SOURCE)))
print("ast.NodeTransformer (2 * 3 -> 6):", [l.strip() for l in folded.splitlines() if "print" in l][0])


# --- 5. o limite da recursão: a pilha explícita ---
def deep(n):
    node = Num(1)
    for _ in range(n):
        node = Add(node, Num(1))
    return node


def evaluate_iter(root):
    """Sem recursão: uma pilha explícita de 'o que falta fazer'."""
    values, stack = [], [root]
    while stack:
        node = stack.pop()
        match node:
            case Num(v):
                values.append(v)
            case Add(l, r):
                stack.extend(["+", r, l])                   # o que falta: avaliar l, avaliar r e, por fim, somar
            case Mul(l, r):
                stack.extend(["*", r, l])
            case "+":
                b, a = values.pop(), values.pop()
                values.append(a + b)
            case "*":
                b, a = values.pop(), values.pop()
                values.append(a * b)
    return values[0]


chain = deep(5_000)
try:
    evaluate(chain, {})
except RecursionError:
    print("\nárvore com 5.000 níveis, visitante recursivo: RecursionError", "| com pilha explícita:", evaluate_iter(chain))


# --- 6. o custo ---
def build(depth):
    if depth == 0:
        return Num(1)
    left, right = build(depth - 1), build(depth - 1)
    return Add(left, right) if depth % 2 else Mul(left, right)


def ev_match(node):
    match node:
        case Num(v):
            return v
        case Var(n):
            return {}[n]
        case Add(l, r):
            return ev_match(l) + ev_match(r)
        case Mul(l, r):
            return ev_match(l) * ev_match(r)
        case Neg(o):
            return -ev_match(o)


def ev_isinstance(node):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Add):
        return ev_isinstance(node.left) + ev_isinstance(node.right)
    if isinstance(node, Mul):
        return ev_isinstance(node.left) * ev_isinstance(node.right)
    raise TypeError


TABLE = {}


def ev_table(node):
    return TABLE[type(node)](node)


TABLE[Num] = lambda n: n.value
TABLE[Add] = lambda n: ev_table(n.left) + ev_table(n.right)
TABLE[Mul] = lambda n: ev_table(n.left) * ev_table(n.right)

big = build(9)                                              # 1.023 nós


def best(fn, n=300):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print(f"\n1.023 nós | singledispatch {best(lambda: evaluate(big, {})):5.0f} µs | match {best(lambda: ev_match(big)):5.0f} µs | isinstance {best(lambda: ev_isinstance(big)):5.0f} µs | tabela por tipo {best(lambda: ev_table(big)):5.0f} µs | pilha explícita {best(lambda: evaluate_iter(big)):5.0f} µs")
