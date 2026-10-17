"""Gabarito do exercício 3."""
import ast


def imports_of(module, source, package):
    tree = ast.parse(source)
    package_parts = module.split(".")[:-1]
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package_parts[: len(package_parts) - (node.level - 1)]
                name = ".".join(base + ([node.module] if node.module else []))
            else:
                name = node.module or ""
            if not name:
                continue
            found.add(name)
            found |= {f"{name}.{a.name}" for a in node.names if a.name != "*"}
    return {n for n in found if (n == package or n.startswith(package + ".")) and n != module}


def _resolve(name, known):
    parts = name.split(".")
    while parts:
        candidate = ".".join(parts)
        if candidate in known:
            return candidate
        parts.pop()
    return None


def _graph(sources, package):
    known = set(sources)
    graph = {}
    for module, source in sources.items():
        deps = {_resolve(n, known) for n in imports_of(module, source, package)}
        graph[module] = {d for d in deps if d and d != module}
    return graph


def _layer(module, layers):
    parts = module.split(".")
    return layers.index(parts[1]) if len(parts) >= 2 and parts[1] in layers else None


def layer_violations(sources, layers, package):
    found = set()
    for module, deps in _graph(sources, package).items():
        mine = _layer(module, layers)
        for dep in deps:
            theirs = _layer(dep, layers)
            if mine is not None and theirs is not None and theirs > mine:
                found.add((module, dep))
    return sorted(found)


def find_cycles(sources, package):
    graph = _graph(sources, package)
    cycles, seen_keys = [], set()

    def visit(node, path):
        if node in path:
            cycle = path[path.index(node):]
            start = cycle.index(min(cycle))
            normalized = cycle[start:] + cycle[:start]
            key = tuple(normalized)
            if key not in seen_keys:
                seen_keys.add(key)
                cycles.append(normalized + [normalized[0]])
            return
        for dep in sorted(graph.get(node, ())):
            visit(dep, path + [node])

    for node in sorted(graph):
        visit(node, [])
    return sorted(cycles)
