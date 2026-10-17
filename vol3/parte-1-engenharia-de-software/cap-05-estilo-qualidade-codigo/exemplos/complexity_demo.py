"""Complexidade ciclomática: contar os caminhos de decisão."""
import ast
import subprocess
import sys
import tempfile
from pathlib import Path

NESTED = """
def shipping(country, weight, express, member):
    if country == "BR":
        if weight < 1:
            if express:
                return 20
            return 10
        elif weight < 5:
            if express:
                return 35
            return 18
        else:
            if member and not express:
                return 25
            return 50
    elif country == "US":
        if weight < 1:
            return 40 if express else 30
        return 80 if express else 60
    else:
        return None
"""

TABLE = """
RATES = {
    ("BR", "light"): (10, 20), ("BR", "medium"): (18, 35), ("BR", "heavy"): (50, 50),
    ("US", "light"): (30, 40), ("US", "medium"): (60, 80), ("US", "heavy"): (60, 80),
}

def band(weight):
    return "light" if weight < 1 else "medium" if weight < 5 else "heavy"

def shipping(country, weight, express, member):
    rates = RATES.get((country, band(weight)))
    if rates is None:
        return None
    if country == "BR" and band(weight) == "heavy" and member and not express:
        return 25
    return rates[1] if express else rates[0]
"""


def complexity(source):
    """1 + decisões: if/elif, for, while, except, ?: , and/or, compreensões, cases."""
    result = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef):
            score = 1
            for inner in ast.walk(node):
                if isinstance(inner, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.IfExp)):
                    score += 1
                elif isinstance(inner, ast.BoolOp):
                    score += len(inner.values) - 1
                elif isinstance(inner, ast.comprehension):
                    score += 1 + len(inner.ifs)
            result[node.name] = score
    return result


for label, source in [("aninhado", NESTED), ("tabela", TABLE)]:
    print(f"{label}: nosso contador {complexity(source)['shipping']}", end=" | ")
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "mod.py"
        path.write_text(source, encoding="utf-8")
        out = subprocess.run([sys.executable, "-m", "radon", "cc", str(path), "-s"], capture_output=True, text=True).stdout
        line = [l for l in out.splitlines() if "shipping" in l][0].strip()
        print("radon:", line.split(" - ", 1)[1])

# Mesma entrada, mesmo resultado nas duas versões
ns_a, ns_b = {}, {}
exec(NESTED, ns_a)
exec(TABLE, ns_b)
cases = [(c, w, e, m) for c in ("BR", "US", "AR") for w in (0.5, 2, 7) for e in (True, False) for m in (True, False)]
differences = [(args, ns_a["shipping"](*args), ns_b["shipping"](*args)) for args in cases if ns_a["shipping"](*args) != ns_b["shipping"](*args)]
print("casos comparados:", len(cases), "| diferenças:", differences[:3])
