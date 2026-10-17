"""Ferramentas para MEDIR e FISCALIZAR uma arquitetura: o grafo de imports, as regras de dependência e os ciclos."""
import ast
from pathlib import Path


def module_name(root: Path, file: Path) -> str:
    parts = file.relative_to(root.parent).with_suffix("").parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def import_graph(package: Path) -> dict[str, set[str]]:
    """Para cada módulo do pacote, os módulos DO PRÓPRIO PACOTE que ele importa (só imports internos)."""
    root_name = package.name
    graph: dict[str, set[str]] = {}
    for file in sorted(package.rglob("*.py")):
        name = module_name(package, file)
        tree = ast.parse(file.read_text(encoding="utf-8"))
        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                deps |= {a.name for a in node.names if a.name.split(".")[0] == root_name}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0 and node.module.split(".")[0] == root_name:
                deps.add(node.module)
                deps |= {f"{node.module}.{a.name}" for a in node.names}
        graph[name] = {d for d in deps if d != name}
    known = set(graph)
    return {m: {d for d in deps if d in known} for m, deps in graph.items()}


def layer_of(module: str, layers: list[str]) -> int | None:
    """O índice da camada (0 = mais interna) a que o módulo pertence, pelo prefixo ``pacote.<camada>``."""
    parts = module.split(".")
    for index, layer in enumerate(layers):
        if len(parts) > 1 and parts[1] == layer or module.endswith("." + layer) and layer in parts:
            return index
    return None


def violations(graph: dict[str, set[str]], layers: list[str]) -> list[tuple[str, str]]:
    """Imports que apontam de uma camada interna para uma EXTERNA (a regra de dependência quebrada)."""
    found = []
    for module, deps in graph.items():
        mine = layer_of(module, layers)
        for dep in deps:
            theirs = layer_of(dep, layers)
            if mine is not None and theirs is not None and theirs > mine:
                found.append((module, dep))
    return sorted(found)


def cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Ciclos de importação (A importa B que importa A), cada um como a lista de módulos."""
    seen, found = set(), []

    def visit(node, path):
        if node in path:
            cycle = path[path.index(node):] + [node]
            if sorted(cycle[:-1]) not in [sorted(c[:-1]) for c in found]:
                found.append(cycle)
            return
        if node in seen:
            return
        seen.add(node)
        for dep in sorted(graph.get(node, ())):
            visit(dep, path + [node])

    for node in sorted(graph):
        visit(node, [])
    return found


def coupling(graph: dict[str, set[str]]) -> dict[str, tuple[int, int]]:
    """Por módulo: (aferente, eferente) = (quantos dependem dele, de quantos ele depende)."""
    return {m: (sum(m in deps for deps in graph.values()), len(deps)) for m, deps in graph.items()}
