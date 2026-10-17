"""Mede o custo de importar modulos da stdlib com -X importtime."""
import subprocess
import sys

MODULES = ["json", "re", "typing", "dataclasses", "decimal", "sqlite3",
           "argparse", "email.message", "http.client", "asyncio"]


def import_cost_us(module: str) -> int:
    """Tempo cumulativo (us) do import, em um interpretador novo."""
    out = subprocess.run(
        [sys.executable, "-X", "importtime", "-c", f"import {module}"],
        capture_output=True, text=True)
    for line in out.stderr.splitlines():
        cells = [c.strip() for c in line.removeprefix("import time:").split("|")]
        if cells[-1] == module:
            return int(cells[1])     # coluna 'cumulative'
    raise RuntimeError(f"{module} nao encontrado")


if __name__ == "__main__":
    rows = []
    for module in MODULES:
        best = min(import_cost_us(module) for _ in range(5))
        rows.append((module, best))
    for module, us in sorted(rows, key=lambda r: -r[1]):
        print(f"{module:14} {us / 1000:7.1f} ms")
