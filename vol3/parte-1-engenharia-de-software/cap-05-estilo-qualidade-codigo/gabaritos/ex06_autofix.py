"""Gabarito do exercício 6."""
import ast


def remove_unused_imports(source):
    tree = ast.parse(source)
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                used |= {e.value for e in node.value.elts if isinstance(e, ast.Constant)}
    lines = source.split("\n")
    edits = {}
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)) or node.lineno != node.end_lineno:
            continue
        if isinstance(node, ast.ImportFrom) and (node.module == "__future__" or any(a.name == "*" for a in node.names)):
            continue
        keep = [a for a in node.names if (a.asname or a.name.split(".")[0] if isinstance(node, ast.Import) else a.asname or a.name) in used]
        if len(keep) == len(node.names):
            continue
        indent = lines[node.lineno - 1][: node.col_offset]
        if not keep:
            edits[node.lineno - 1] = None
            continue
        names = ", ".join(a.name + (f" as {a.asname}" if a.asname else "") for a in keep)
        head = f"import {names}" if isinstance(node, ast.Import) else f"from {'.' * node.level}{node.module or ''} import {names}"
        edits[node.lineno - 1] = indent + head
    out = []
    for index, line in enumerate(lines):
        if index in edits:
            if edits[index] is None:
                continue
            out.append(edits[index])
        else:
            out.append(line)
    return "\n".join(out)
