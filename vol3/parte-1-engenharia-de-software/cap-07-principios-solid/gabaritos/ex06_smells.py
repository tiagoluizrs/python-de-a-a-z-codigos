"""Gabarito do exercício 6."""
import ast
import textwrap
from dataclasses import dataclass

INFRA = {"SMTP", "SMTP_SSL", "connect", "Session", "Client", "Redis", "MongoClient", "create_engine", "urlopen"}


@dataclass(frozen=True)
class Smell:
    kind: str
    where: str
    line: int


def _call_name(call):
    f = call.func
    if isinstance(f, ast.Name):
        return f.id, None
    if isinstance(f, ast.Attribute):
        base = f.value.id if isinstance(f.value, ast.Name) else None
        return f.attr, base
    return None, None


def _compared_name(test):
    """O nome comparado com constantes em uma condição, ou None."""
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.left, ast.Name):
        op, right = test.ops[0], test.comparators[0]
        if isinstance(op, ast.Eq) and isinstance(right, ast.Constant):
            return test.left.id
        if isinstance(op, ast.In) and isinstance(right, (ast.Tuple, ast.List, ast.Set)) and all(isinstance(e, ast.Constant) for e in right.elts):
            return test.left.id
    return None


def _walk_function(func, where, bases, in_class, out):
    chain_roots = set()
    for node in _own(func):
        if isinstance(node, ast.If) and id(node) not in chain_roots:
            names, current, branches = [], node, 0
            while True:
                names.append(_compared_name(current.test))
                branches += 1
                chain_roots.add(id(current))
                if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                    current = current.orelse[0]
                else:
                    break
            if branches >= 4 and names[0] is not None and all(n == names[0] for n in names):
                out.append(Smell("OCP", where, node.lineno))
        if isinstance(node, ast.Raise) and in_class and bases:
            exc = node.exc
            target = exc.func if isinstance(exc, ast.Call) else exc
            if isinstance(target, ast.Name) and target.id == "NotImplementedError":
                out.append(Smell("LSP", where, node.lineno))
        if isinstance(node, ast.Call):
            name, base = _call_name(node)
            if name in INFRA or (name in ("now", "utcnow") and base == "datetime") or (name == "time" and base == "time"):
                out.append(Smell("DIP", where, node.lineno))


def _own(func):
    """Nós da função, sem descer para funções ou classes aninhadas (elas são analisadas à parte)."""
    stack = list(ast.iter_child_nodes(func))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(node))


def find_smells(source):
    tree = ast.parse(textwrap.dedent(source))
    out = []

    def visit(node, class_name=None, bases=False):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                visit(child, child.name, bool(child.bases))
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                where = f"{class_name}.{child.name}" if class_name and isinstance(node, ast.ClassDef) else child.name
                _walk_function(child, where, bases if isinstance(node, ast.ClassDef) else False, isinstance(node, ast.ClassDef), out)
                visit(child, None, False)
            else:
                visit(child, class_name, bases)

    visit(tree)
    return sorted(set(out), key=lambda s: (s.line, s.kind, s.where))
