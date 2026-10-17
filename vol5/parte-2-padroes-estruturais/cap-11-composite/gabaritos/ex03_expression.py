"""Gabarito do exercício 3."""
from dataclasses import dataclass


class Expr:
    prec = 10

    def evaluate(self, env):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError

    def simplify(self):
        raise NotImplementedError


def _wrap(child, parent_prec, right=False):
    text = str(child)
    if child.prec < parent_prec or (right and child.prec == parent_prec):
        return f"({text})"
    return text


@dataclass(frozen=True)
class Num(Expr):
    value: float

    def evaluate(self, env):
        return self.value

    def variables(self):
        return set()

    def simplify(self):
        return self

    def __str__(self):
        return repr(self.value)


@dataclass(frozen=True)
class Var(Expr):
    name: str

    def evaluate(self, env):
        if self.name not in env:
            raise NameError(f"variável indefinida: {self.name}")
        return env[self.name]

    def variables(self):
        return {self.name}

    def simplify(self):
        return self

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Add(Expr):
    left: Expr
    right: Expr
    prec = 1

    def evaluate(self, env):
        return self.left.evaluate(env) + self.right.evaluate(env)

    def variables(self):
        return self.left.variables() | self.right.variables()

    def simplify(self):
        left, right = self.left.simplify(), self.right.simplify()
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value + right.value)
        if left == Num(0):
            return right
        if right == Num(0):
            return left
        return Add(left, right)

    def __str__(self):
        return f"{_wrap(self.left, 1)} + {_wrap(self.right, 1, right=True)}"


@dataclass(frozen=True)
class Mul(Expr):
    left: Expr
    right: Expr
    prec = 2

    def evaluate(self, env):
        return self.left.evaluate(env) * self.right.evaluate(env)

    def variables(self):
        return self.left.variables() | self.right.variables()

    def simplify(self):
        left, right = self.left.simplify(), self.right.simplify()
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value * right.value)
        if left == Num(0) or right == Num(0):
            return Num(0)
        if left == Num(1):
            return right
        if right == Num(1):
            return left
        return Mul(left, right)

    def __str__(self):
        return f"{_wrap(self.left, 2)} * {_wrap(self.right, 2, right=True)}"


@dataclass(frozen=True)
class Neg(Expr):
    operand: Expr
    prec = 3

    def evaluate(self, env):
        return -self.operand.evaluate(env)

    def variables(self):
        return self.operand.variables()

    def simplify(self):
        inner = self.operand.simplify()
        if isinstance(inner, Num):
            return Num(-inner.value)
        if isinstance(inner, Neg):
            return inner.operand
        return Neg(inner)

    def __str__(self):
        return "-" + _wrap(self.operand, 3)
