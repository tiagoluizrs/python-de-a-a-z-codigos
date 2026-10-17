"""A saída do pytest quando um teste falha (assertion rewriting) e as opções do dia a dia."""
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS = """
def test_list():
    assert [1, 2, 3, 4] == [1, 2, 9, 4]

def test_dict():
    assert {"a": 1, "b": 2} == {"a": 1, "b": 3, "c": 4}

def test_text():
    assert "olá, mundo" == "olá, Mundo"

def test_membership():
    users = ["ana", "bia"]
    assert "caio" in users

def test_message():
    age = 17
    assert age >= 18, "menor de idade"

def test_ok():
    assert 1 + 1 == 2
"""

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "test_report.py"
    path.write_text(TESTS, encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "pytest", "test_report.py", "-q", "--no-header", "-p", "no:cacheprovider",
                             "--tb=short", "--rootdir", folder], cwd=folder, capture_output=True, text=True, encoding="utf-8")
    lines = [line for line in result.stdout.splitlines() if line.startswith(("E ", "FAILED", "=")) or " passed" in line or " failed" in line]
    print("\n".join(lines))
    print("código de saída:", result.returncode)
