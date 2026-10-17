"""Rodar as regras de segurança (bandit) do ruff sobre o arquivo de padrões inseguros."""
import re
import subprocess
import sys
from pathlib import Path

target = Path(__file__).resolve().parent.parent / "alvos" / "bad_patterns.py"
result = subprocess.run([sys.executable, "-m", "ruff", "check", "--isolated", "--select", "S", "--output-format", "concise",
                         str(target)], capture_output=True, text=True, encoding="utf-8")
for line in result.stdout.splitlines():
    match = re.match(r".*bad_patterns.py:(\d+):\d+: (S\d+) (.*)", line)
    if match:
        print(f"linha {match.group(1):>2} {match.group(2)} {match.group(3)[:70]}")
print(result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "sem achados")
