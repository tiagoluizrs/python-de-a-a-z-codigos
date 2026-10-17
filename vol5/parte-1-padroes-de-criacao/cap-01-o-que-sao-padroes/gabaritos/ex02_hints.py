"""Gabarito do exercício 2."""
import ast
import textwrap
from dataclasses import dataclass

OBSERVER_NAMES = {"observers", "listeners", "subscribers", "handlers", "callbacks"}


@dataclass(frozen=True)
class Hint:
    pattern: str
    where: str
    line: int


def _is_empty_collection(value):
    if isinstance(value, (ast.List, ast.Set)) and not value.elts:
        return True
    return isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in ("list", "set") and not value.args


def pattern_hints(source):
    tree = ast.parse(textwrap.dedent(source))
    hints = []
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        methods = [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        names = {m.name for m in methods}
        public = [m.name for m in methods if not m.name.startswith("_")]
        others = names - {"__init__", "__call__"} - set(public)
        if (len(public) == 1 and not others and "__call__" not in names) or (not public and "__call__" in names and not others):
            hints.append(Hint("Strategy/Command", cls.name, cls.lineno))
        assigned = set()
        for node in cls.body:
            if isinstance(node, ast.Assign):
                assigned |= {t.id for t in node.targets if isinstance(t, ast.Name)}
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                assigned.add(node.target.id)
        if assigned & {"_instance", "__instance"} or "__new__" in names:
            hints.append(Hint("Singleton", cls.name, cls.lineno))
        if {"__iter__", "__next__"} <= names:
            hints.append(Hint("Iterator", cls.name, cls.lineno))
        found = False
        for m in methods:
            for node in ast.walk(m):
                if isinstance(node, ast.Assign) and _is_empty_collection(node.value):
                    for t in node.targets:
                        if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self" and t.attr in OBSERVER_NAMES:
                            found = True
        if found:
            hints.append(Hint("Observer", cls.name, cls.lineno))
    return sorted(hints, key=lambda h: (h.line, h.pattern))
