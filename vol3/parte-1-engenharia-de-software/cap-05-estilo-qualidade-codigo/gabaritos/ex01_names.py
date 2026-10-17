"""Gabarito do exercício 1."""
import ast
import re

CLASS = re.compile(r"^_?[A-Z][A-Za-z0-9]*$")
FUNC = re.compile(r"^_*[a-z][a-z0-9_]*_*$|^__[a-z0-9_]+__$")


def check_names(source):
    findings = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not CLASS.match(node.name):
                findings.append((node.lineno, "N801", node.name))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not FUNC.match(node.name):
                findings.append((node.lineno, "N802", node.name))
            args = node.args
            every = args.posonlyargs + args.args + args.kwonlyargs + [a for a in (args.vararg, args.kwarg) if a]
            for arg in every:
                if arg.arg not in ("self", "cls") and arg.arg != arg.arg.lower():
                    findings.append((arg.lineno, "N803", arg.arg))
            for inner in ast.walk(node):
                if isinstance(inner, ast.Name) and isinstance(inner.ctx, ast.Store) and inner.id != inner.id.lower():
                    findings.append((inner.lineno, "N806", inner.id))
    return sorted(set(findings))
