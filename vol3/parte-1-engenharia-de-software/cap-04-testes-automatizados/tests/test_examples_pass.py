"""Os testes de demonstração da pasta exemplos/ também precisam passar."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_demo_test_suite_passes():
    result = subprocess.run([sys.executable, "-m", "pytest", "exemplos", "-q", "--no-header", "-p", "no:cacheprovider"],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout[-2000:]
    assert " passed" in result.stdout
