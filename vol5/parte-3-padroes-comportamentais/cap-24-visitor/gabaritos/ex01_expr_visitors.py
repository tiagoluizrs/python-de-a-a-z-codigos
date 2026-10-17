"""Gabarito do exercício 1."""
from collections import Counter


class Node:
    def accept(self, visitor):
        raise NotImplementedError


class Num(Node):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_num(self)


class Var(Node):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_var(self)


class Add(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def accept(self, visitor):
        return visitor.visit_add(self)


class Mul(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def accept(self, visitor):
        return visitor.visit_mul(self)


class Neg(Node):
    def __init__(self, operand):
        self.operand = operand

    def accept(self, visitor):
        return visitor.visit_neg(self)


class Evaluator:
    def __init__(self, env):
        self.env = env

    def visit_num(self, node):
        return node.value

    def visit_var(self, node):
        if node.name not in self.env:
            raise KeyError(f"variável indefinida: {node.name}")
        return self.env[node.name]

    def visit_add(self, node):
        return node.left.accept(self) + node.right.accept(self)

    def visit_mul(self, node):
        return node.left.accept(self) * node.right.accept(self)

    def visit_neg(self, node):
        return -node.operand.accept(self)


class Printer:
    ADD, MUL, NEG, ATOM = 1, 2, 3, 4

    def _show(self, node, needed):
        text = node.accept(self)
        return f"({text})" if self._precedence(node) < needed else text

    def _precedence(self, node):
        return {Add: self.ADD, Mul: self.MUL, Neg: self.NEG}.get(type(node), self.ATOM)

    def visit_num(self, node):
        return str(node.value)

    def visit_var(self, node):
        return node.name

    def visit_add(self, node):
        return f"{self._show(node.left, 1)} + {self._show(node.right, 1)}"

    def visit_mul(self, node):
        return f"{self._show(node.left, 2)} * {self._show(node.right, 2)}"

    def visit_neg(self, node):
        return f"-{self._show(node.operand, 3)}"


class VariableCollector:
    def visit_num(self, node):
        return []

    def visit_var(self, node):
        return [node.name]

    def _both(self, node):
        return sorted(set(node.left.accept(self)) | set(node.right.accept(self)))

    visit_add = visit_mul = _both

    def visit_neg(self, node):
        return node.operand.accept(self)


class Depth:
    def visit_num(self, node):
        return 1

    visit_var = visit_num

    def visit_add(self, node):
        return 1 + max(node.left.accept(self), node.right.accept(self))

    visit_mul = visit_add

    def visit_neg(self, node):
        return 1 + node.operand.accept(self)


class CountVisitor:
    def __init__(self):
        self.counts = Counter()

    def visit_num(self, node):
        self.counts["Num"] += 1

    def visit_var(self, node):
        self.counts["Var"] += 1

    def visit_add(self, node):
        self.counts["Add"] += 1
        node.left.accept(self)
        node.right.accept(self)

    def visit_mul(self, node):
        self.counts["Mul"] += 1
        node.left.accept(self)
        node.right.accept(self)

    def visit_neg(self, node):
        self.counts["Neg"] += 1
        node.operand.accept(self)
