"""Os quatro verificadores de tipos, o mesmo arquivo com 9 erros."""
import re
import subprocess
import sys
import time
from pathlib import Path

TARGET = Path(__file__).with_name("errors_demo.py")
CHECKERS = [
    ("mypy", ["mypy", str(TARGET)], r"error:"),
    ("pyright", ["pyright", str(TARGET)], r"- error:"),
    ("ty", ["ty", "check", "--output-format", "concise", str(TARGET)], r"error\["),
    ("pyrefly", ["pyrefly", "check", "--preset", "default", "--output-format", "min-text", str(TARGET)], r"ERROR"),
]

print(f"{'ferramenta':<10}{'erros':>6}{'tempo':>9}   primeira mensagem")
for name, command, pattern in CHECKERS:
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "-m", *command], capture_output=True, text=True, encoding="utf-8")
    elapsed = time.perf_counter() - start
    output = result.stdout + result.stderr
    first = next((line.strip() for line in output.splitlines() if re.search(pattern, line)), "")
    first = re.sub(r"^.*errors_demo.py:", "", first)
    print(f"{name:<10}{len(re.findall(pattern, output)):>6}{elapsed:>8.2f}s   {first[:70]}")
