"""Gabarito do exercício 4."""
import ast


class _Functions(ast.NodeVisitor):
    def __init__(self):
        self.names = []

    def visit_FunctionDef(self, node):
        self.names.append(node.name)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def function_names(source):
    visitor = _Functions()
    visitor.visit(ast.parse(source))
    return visitor.names


class _Imports(ast.NodeVisitor):
    def __init__(self):
        self.modules = set()

    def visit_Import(self, node):
        self.modules.update(alias.name.split(".")[0] for alias in node.names)

    def visit_ImportFrom(self, node):
        if node.level == 0 and node.module:
            self.modules.add(node.module.split(".")[0])


def imported_modules(source):
    visitor = _Imports()
    visitor.visit(ast.parse(source))
    return sorted(visitor.modules)


class _Loops(ast.NodeVisitor):
    def __init__(self):
        self.depth = self.deepest = 0

    def _loop(self, node):
        self.depth += 1
        self.deepest = max(self.deepest, self.depth)
        self.generic_visit(node)
        self.depth -= 1

    visit_For = visit_AsyncFor = visit_While = _loop


def max_loop_depth(source):
    visitor = _Loops()
    visitor.visit(ast.parse(source))
    return visitor.deepest


class _Fold(ast.NodeTransformer):
    OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b}

    @staticmethod
    def _is_int(node):
        return isinstance(node, ast.Constant) and type(node.value) is int

    def visit_BinOp(self, node):
        self.generic_visit(node)
        op = self.OPS.get(type(node.op))
        if op and self._is_int(node.left) and self._is_int(node.right):
            return ast.copy_location(ast.Constant(op(node.left.value, node.right.value)), node)
        return node


def fold_constants(source):
    return ast.unparse(_Fold().visit(ast.parse(source)))
