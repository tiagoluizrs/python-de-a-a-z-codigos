"""Gabarito do exercício 6."""
import ast
from pathlib import Path


def _module_name(root, file):
    parts = list(file.relative_to(root).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def import_graph(src_root, package):
    root = Path(src_root)
    files = sorted((root / package).rglob("*.py"))
    known = {_module_name(root, f) for f in files}
    graph = {}
    for file in files:
        name = _module_name(root, file)
        is_package = file.name == "__init__.py"
        current_package = name if is_package else name.rpartition(".")[0]
        deps = set()
        for node in ast.walk(ast.parse(file.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == package or alias.name.startswith(package + "."):
                        deps.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base_parts = current_package.split(".") if current_package else []
                    base_parts = base_parts[:len(base_parts) - (node.level - 1)]
                    base = ".".join(base_parts + ([node.module] if node.module else []))
                else:
                    base = node.module or ""
                if base != package and not base.startswith(package + "."):
                    continue
                submodules = {f"{base}.{alias.name}" for alias in node.names} & known
                deps.update(submodules or {base})
        graph[name] = {d for d in deps if d in known and d != name}
    return graph


def find_cycle(graph):
    state = {}
    stack = []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            if nxt not in state:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if node not in state:
            found = visit(node)
            if found:
                return found
    return None
