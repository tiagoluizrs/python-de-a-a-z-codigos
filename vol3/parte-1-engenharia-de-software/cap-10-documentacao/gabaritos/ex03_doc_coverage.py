"""Gabarito do exercício 3."""
import ast

FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def docstring_coverage(source):
    tree = ast.parse(source)
    items = [("<module>", ast.get_docstring(tree) is not None)]

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef) and not child.name.startswith("_"):
                name = prefix + child.name
                items.append((name, ast.get_docstring(child) is not None))
                visit(child, name + ".")
            elif isinstance(child, FUNCTIONS) and not child.name.startswith("_"):
                items.append((prefix + child.name, ast.get_docstring(child) is not None))

    visit(tree, "")
    documented = sum(1 for _, has in items if has)
    return documented, len(items), sorted(name for name, has in items if not has)


def percentage(documented, total):
    return 100.0 if total == 0 else round(documented / total * 100, 1)
