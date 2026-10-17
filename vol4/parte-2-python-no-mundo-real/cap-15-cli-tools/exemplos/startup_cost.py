"""O custo que o usuário SENTE: o tempo até o comando responder (importar bibliotecas pesadas é caro)."""
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).parent
ENV = {**os.environ, "TODO_FILE": str(Path(tempfile.mkdtemp(prefix="cli-startup-")) / "t.json"), "PYTHONUTF8": "1"}


def wall(args, repeat=7) -> float:
    """Mediana (ms) do tempo de um processo novo: o que o usuário espera a cada comando."""
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        subprocess.run([sys.executable, *args], capture_output=True, env=ENV, cwd=HERE)
        times.append((time.perf_counter() - start) * 1e3)
    return statistics.median(times)


baseline = wall(["-c", "pass"])
print(f"python -c pass (o piso do interpretador): {baseline:6.0f} ms\n")
print("importar só a biblioteca (acima do piso):")
for module in ("argparse", "json", "click", "typer", "rich", "rich.table", "rich.progress", "textual", "httpx", "pandas"):
    ms = wall(["-c", f"import {module}"]) - baseline
    print(f"  import {module:<14} +{max(ms, 0):6.0f} ms")

print("\ncomando completo (`todo list`, o mesmo núcleo, três interfaces):")
for script in ("todo_argparse.py", "todo_click.py", "todo_typer.py"):
    ms = wall([script, "list"]) - baseline
    print(f"  {script:<18} +{ms:6.0f} ms")

# onde está o tempo do Typer? -X importtime lista cada módulo importado (microssegundos, acumulado)
proc = subprocess.run([sys.executable, "-X", "importtime", "-c", "import typer"], capture_output=True, text=True, env=ENV)
rows = []
for line in proc.stderr.splitlines()[1:]:
    parts = line.split("|")
    if len(parts) == 3 and parts[1].strip().isdigit():
        rows.append((int(parts[1]), parts[2].strip()))
print("\nos 6 imports mais caros ao importar typer (acumulado, ms):")
for cumulative, name in sorted(rows, reverse=True)[:6]:
    print(f"  {cumulative / 1e3:7.1f}  {name}")

# a defesa: importe o que é pesado SÓ dentro do comando que precisa dele
script = '''
import argparse, sys
def main(argv):
    p = argparse.ArgumentParser(prog="demo")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("version")
    sub.add_parser("report")
    args = p.parse_args(argv)
    if args.cmd == "version":
        print("1.0")
    else:
        import json, decimal, statistics                  # imports pesados ficam dentro do comando
        import pandas as pd
        print(pd.__version__)
main(sys.argv[1:])
'''
tmp = Path(tempfile.mkdtemp(prefix="cli-lazy-")) / "demo.py"
tmp.write_text(script, encoding="utf-8")
t_version = wall([str(tmp), "version"]) - baseline
t_report = wall([str(tmp), "report"]) - baseline
print(f"\nimport tardio: `demo version` +{t_version:.0f} ms (não paga o pandas) | `demo report` +{t_report:.0f} ms (paga, mas só ele)")
