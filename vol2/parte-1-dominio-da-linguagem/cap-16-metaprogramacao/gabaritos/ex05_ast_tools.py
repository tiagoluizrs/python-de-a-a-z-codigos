"""Gabarito do exercício 5."""
import ast


class _Calls(ast.NodeVisitor):
    def __init__(self):
        self.names = []                     # (nome, é_nome_simples)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.names.append((node.func.id, True))
        elif isinstance(node.func, ast.Attribute):
            self.names.append((node.func.attr, False))
        self.generic_visit(node)


def called_names(source):
    visitor = _Calls()
    visitor.visit(ast.parse(source))
    return sorted({name for name, _ in visitor.names})


def has_unsafe_calls(source, forbidden=("eval", "exec", "compile", "__import__")):
    visitor = _Calls()
    visitor.visit(ast.parse(source))
    return any(simple and name in forbidden for name, simple in visitor.names)


class _Upper(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return ast.copy_location(ast.Constant(node.value.upper()), node)
        return node


def constants_to_upper(source):
    tree = _Upper().visit(ast.parse(source))
    return ast.unparse(ast.fix_missing_locations(tree))
