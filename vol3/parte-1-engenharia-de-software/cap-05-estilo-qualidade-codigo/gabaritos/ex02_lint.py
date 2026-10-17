"""Gabarito do exercício 2."""
import ast


def _is_mutable_default(node):
    if isinstance(node, (ast.List, ast.Dict, ast.Set)):
        return True
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ("list", "dict", "set") and not node.args and not node.keywords)


def lint(source):
    tree = ast.parse(source)
    findings = []
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                used |= {e.value for e in node.value.elts if isinstance(e, ast.Constant)}
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append((node.lineno, "E722"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
            findings += [(d.lineno, "B006") for d in defaults if _is_mutable_default(d)]
        elif isinstance(node, ast.Compare):
            for op, right in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(right, ast.Constant):
                    if right.value is None:
                        findings.append((node.lineno, "E711"))
                    elif right.value is True or right.value is False:
                        findings.append((node.lineno, "E712"))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                if name not in used:
                    findings.append((node.lineno, "F401"))
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            for alias in node.names:
                name = alias.asname or alias.name
                if name != "*" and name not in used:
                    findings.append((node.lineno, "F401"))
    return sorted(findings)
