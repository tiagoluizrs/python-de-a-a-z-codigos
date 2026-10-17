"""Cobertura de linhas e de ramos: 100% de linhas não significa testado."""
import subprocess
import sys
import tempfile
from pathlib import Path

MODULE = """
def classify(n):
    label = "neg" if n < 0 else "other"
    if n % 2 == 0:
        label += "-even"
    return label
"""
TESTS = """
from mod import classify

def test_negative_even():
    assert classify(-2) == "neg-even"
"""

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    (root / "mod.py").write_text(MODULE, encoding="utf-8")
    (root / "test_mod.py").write_text(TESTS, encoding="utf-8")
    env = {"PYTHONPATH": folder, "COVERAGE_FILE": str(root / ".cov")}

    def run(*args):
        import os
        return subprocess.run([sys.executable, "-m", *args], cwd=folder, capture_output=True, text=True,
                              env={**os.environ, **env}, encoding="utf-8")

    run("coverage", "run", "--branch", "--source", folder, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", folder)
    report = run("coverage", "report", "-m").stdout
    print("\n".join(line for line in report.splitlines() if line.strip() and not line.startswith("---")))
