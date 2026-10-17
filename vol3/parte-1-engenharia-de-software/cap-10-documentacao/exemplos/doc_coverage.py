"""Cobertura de documentação: interrogate (docstrings) e ruff (regras D)."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

result = subprocess.run([sys.executable, "-m", "interrogate", "-v", "src"], capture_output=True, text=True, cwd=ROOT, encoding="utf-8")
for line in result.stdout.splitlines():
    if "%" in line or "RESULT" in line:
        print(line.strip())

# Um arquivo mal documentado, para o ruff acusar
BAD = '''def f(x):
    return x

class K:
    def m(self):
        """sem ponto no fim e sem imperativo"""
        return 1

def g():
    """Faz algo.
    Sem linha em branco depois do resumo."""
'''
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "bad.py"
    path.write_text(BAD, encoding="utf-8")
    out = subprocess.run([sys.executable, "-m", "ruff", "check", "--isolated", "--select", "D", "--output-format", "concise", str(path)],
                         capture_output=True, text=True, encoding="utf-8").stdout
    for line in out.splitlines():
        match = re.match(r".*bad.py:(\d+):\d+: (D\d+) (.*)", line)
        if match:
            print(f"linha {match.group(1):>2} {match.group(2)} {match.group(3)[:60]}")
