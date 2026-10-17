"""Gabarito do exercício 1."""
import ast
import textwrap


def _is_abstract(cls):
    for base in cls.bases:
        name = base.id if isinstance(base, ast.Name) else base.attr if isinstance(base, ast.Attribute) else None
        if name == "ABC":
            return True
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for deco in node.decorator_list:
                name = deco.id if isinstance(deco, ast.Name) else deco.attr if isinstance(deco, ast.Attribute) else None
                if name == "abstractmethod":
                    return True
    return False


def measure(source):
    text = textwrap.dedent(source)
    tree = ast.parse(text)
    classes = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

    def depth(cls, seen=()):
        bases = [classes[b.id] for b in cls.bases if isinstance(b, ast.Name) and b.id in classes and b.id not in seen]
        return 1 + max((depth(b, seen + (cls.name,)) for b in bases), default=0)

    return {
        "lines": sum(1 for l in text.splitlines() if l.strip() and not l.strip().startswith("#")),
        "classes": len(classes),
        "functions": sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) for n in ast.walk(tree)),
        "abstract": sum(_is_abstract(c) for c in classes.values()),
        "depth": max((depth(c) for c in classes.values()), default=0),
    }


def ceremony_ratio(classic, pythonic):
    py = measure(pythonic)["lines"]
    if py == 0:
        raise ValueError("código pythônico sem linhas")
    return round(measure(classic)["lines"] / py, 1)
