"""O exemplo de tipagem moderna precisa passar no mypy --strict e rodar."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_clean_typed_passes_strict_mypy(tmp_path):
    result = subprocess.run([sys.executable, "-m", "mypy", "--strict", "--no-incremental", "--cache-dir", str(tmp_path),
                             "exemplos/clean_typed.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr


def test_clean_typed_runs():
    result = subprocess.run([sys.executable, "exemplos/clean_typed.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0 and "leitura" not in result.stderr, result.stderr
    assert "escrita" in result.stdout
