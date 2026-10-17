"""Gabarito do exercício 1."""
import ast
import textwrap


def _classes(source):
    return [n for n in ast.walk(ast.parse(textwrap.dedent(source))) if isinstance(n, ast.ClassDef)]


def _own_nodes(method):
    """Os nós do método, sem descer para classes aninhadas."""
    stack = list(ast.iter_child_nodes(method))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, ast.ClassDef):
            stack.extend(ast.iter_child_nodes(node))


def _groups(cls):
    methods = {m.name: m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name != "__init__"}
    parent = {m: m for m in methods}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owners: dict[str, list[str]] = {}
    for name, method in methods.items():
        for node in _own_nodes(method):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
                if node.attr in methods:
                    parent[find(name)] = find(node.attr)
                else:
                    owners.setdefault(node.attr, []).append(name)
    for names in owners.values():
        for other in names[1:]:
            parent[find(other)] = find(names[0])
    groups: dict[str, list[str]] = {}
    for name in methods:
        groups.setdefault(find(name), []).append(name)
    return [sorted(g) for g in groups.values()]


def lcom4(source):
    return {cls.name: len(_groups(cls)) for cls in _classes(source)}


def split_candidates(source, threshold=2):
    return sorted(name for name, n in lcom4(source).items() if n >= threshold)


def attribute_groups(source, class_name):
    for cls in _classes(source):
        if cls.name == class_name:
            return sorted(_groups(cls), key=lambda g: g[0])
    raise KeyError(class_name)
