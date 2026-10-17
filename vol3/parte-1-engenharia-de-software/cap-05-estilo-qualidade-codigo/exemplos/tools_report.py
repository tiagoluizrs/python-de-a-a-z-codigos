"""As mesmas ferramentas, o mesmo arquivo: o que cada uma encontra."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
MESSY, CLEAN = HERE / "messy.py", HERE / "clean.py"


def run(*args):
    result = subprocess.run([sys.executable, "-m", *args], capture_output=True, text=True, encoding="utf-8")
    return result.stdout + result.stderr


def count(output, pattern):
    return len(re.findall(pattern, output, re.M))


for path in (MESSY, CLEAN):
    print(f"=== {path.name}")
    ruff = run("ruff", "check", "--isolated", "--select", "E,F,W,I,B,UP,SIM,N,C4,RET,PL", "--output-format", "concise", str(path))
    print("ruff check (E,F,W,I,B,UP,SIM,N,C4,RET,PL):", count(ruff, r"^\S+:\d+:\d+:"), "achados")
    fmt = run("ruff", "format", "--isolated", "--check", str(path))
    print("ruff format --check:", fmt.strip().splitlines()[0] if fmt.strip() else "ok")
    pyc = run("pycodestyle", str(path))
    print("pycodestyle (79 colunas):", count(pyc, r"^\S+:\d+:\d+:"), "achados")
    flakes = run("pyflakes", str(path))
    print("pyflakes:", count(flakes, r"^\S+:\d+:\d+"), "achados")
    pylint = run("pylint", str(path), "--disable=C0114")
    rating = re.search(r"rated at ([\d.]+)/10", pylint)
    print("pylint:", count(pylint, r"^\S+:\d+:\d+: [CRWEF]\d+"), "achados | nota", rating.group(1) if rating else "?")

print("--- ruff, estatísticas por regra em messy.py")
stats = run("ruff", "check", "--isolated", "--select", "E,F,W,I,B,UP,SIM,N,C4,RET,PL", "--statistics", str(MESSY))
for line in stats.splitlines():
    if re.match(r"^\d+\s", line):
        print("  ", " ".join(line.split()))
