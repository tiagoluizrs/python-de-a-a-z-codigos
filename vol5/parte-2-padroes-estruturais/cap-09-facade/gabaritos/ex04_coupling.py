"""Gabarito do exercício 4."""
import ast
import textwrap


def _own(func):
    stack = list(ast.iter_child_nodes(func))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(node))


def _names(handler_type):
    if isinstance(handler_type, ast.Name):
        return [handler_type.id]
    if isinstance(handler_type, ast.Tuple):
        return [e.id for e in handler_type.elts if isinstance(e, ast.Name)]
    return []


def _known(func):
    known = set()
    for node in _own(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            known.add(f"{node.func.value.id}.{node.func.attr}")
        elif isinstance(node, ast.ExceptHandler):
            known.update(_names(node.type))
    return sorted(known)


def coupling(source):
    tree = ast.parse(textwrap.dedent(source))
    out = {}

    def visit(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                visit(child, f"{child.name}.")
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[prefix + child.name] = _known(child)
            else:
                visit(child, prefix)

    visit(tree)
    return out


def facade_gain(before, after, function):
    b, a = coupling(before), coupling(after)
    if function not in b or function not in a:
        raise KeyError(function)
    return len(b[function]) - len(a[function])


def most_coupled(source, top=3):
    items = [(name, len(calls)) for name, calls in coupling(source).items() if calls]
    items.sort(key=lambda item: (-item[1], item[0]))
    return items[:top]
