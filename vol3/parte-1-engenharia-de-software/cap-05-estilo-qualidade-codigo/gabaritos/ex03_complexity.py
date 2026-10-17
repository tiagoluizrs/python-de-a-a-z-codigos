"""Gabarito do exercício 3."""
import ast

FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def _score(function):
    score = 1
    stack = list(ast.iter_child_nodes(function))
    while stack:
        node = stack.pop()
        if isinstance(node, FUNCTIONS + (ast.Lambda,)):
            continue                                       # função interna tem pontuação própria
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp, ast.match_case)):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            score += 1 + len(node.ifs)
        stack.extend(ast.iter_child_nodes(node))
    return score


def cyclomatic_complexity(source):
    result = {}

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, FUNCTIONS):
                name = f"{prefix}{child.name}"
                result[name] = _score(child)
                visit(child, name + ".")
            elif isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")
            else:
                visit(child, prefix)

    visit(ast.parse(source), "")
    return result


def too_complex(source, limit=10):
    return sorted(name for name, score in cyclomatic_complexity(source).items() if score > limit)
