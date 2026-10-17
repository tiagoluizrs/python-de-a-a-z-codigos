"""Importações absolutas e relativas dentro de um pacote."""
import ast
import inspect
from pathlib import Path

import inventory

package = Path(inspect.getfile(inventory)).parent
for name in ("__init__", "cli", "storage", "core"):
    tree = ast.parse((package / f"{name}.py").read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            dots = "." * node.level
            imports.append(f"from {dots}{node.module or ''} import {', '.join(a.name for a in node.names)}")
        elif isinstance(node, ast.Import):
            imports.append("import " + ", ".join(a.name for a in node.names))
    print(f"{name}.py:")
    for line in imports:
        print("   ", line)
