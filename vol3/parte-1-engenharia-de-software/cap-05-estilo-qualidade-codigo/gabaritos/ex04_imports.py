"""Gabarito do exercício 4."""
import ast
import sys


def _section(node, module):
    if isinstance(node, ast.ImportFrom) and node.level:
        return 3
    top = module.split(".")[0]
    if top == "__future__":
        return 0
    return 1 if top in sys.stdlib_module_names else 2


def sort_imports(source):
    entries = []
    for node in ast.parse(source).body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                text = f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                entries.append((_section(node, alias.name), 0, alias.name.lower(), text))
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            names = sorted(node.names, key=lambda a: a.name.lower())
            joined = ", ".join(a.name + (f" as {a.asname}" if a.asname else "") for a in names)
            entries.append((_section(node, node.module or ""), 1, module.lower(), f"from {module} import {joined}"))
    if not entries:
        return ""
    entries.sort(key=lambda e: e[:3])
    lines = []
    previous = None
    for section, _, _, text in entries:
        if previous is not None and section != previous:
            lines.append("")
        lines.append(text)
        previous = section
    return "\n".join(lines) + "\n"
