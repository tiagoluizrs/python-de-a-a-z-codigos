"""Gabarito do exercicio 5: custo de import."""
import subprocess
import sys


def parse_importtime(stderr: str, module: str) -> int:
    for line in stderr.splitlines():
        if not line.startswith("import time:"):
            continue
        body = line.removeprefix("import time:")
        cells = [c.strip() for c in body.split("|")]
        if len(cells) == 3 and cells[2] == module:
            return int(cells[1])          # coluna 'cumulative'
    raise ValueError(f"{module!r} nao aparece na saida")


def _cost(module: str) -> int:
    out = subprocess.run(
        [sys.executable, "-X", "importtime", "-c", f"import {module}"],
        capture_output=True, text=True, check=True)
    return parse_importtime(out.stderr, module)


def most_expensive(modules: list[str]) -> tuple[str, int]:
    # Melhor de 3 tentativas reduz o ruido do disco e do sistema
    costs = {m: min(_cost(m) for _ in range(3)) for m in modules}
    name = max(costs, key=costs.get)
    return name, costs[name]
