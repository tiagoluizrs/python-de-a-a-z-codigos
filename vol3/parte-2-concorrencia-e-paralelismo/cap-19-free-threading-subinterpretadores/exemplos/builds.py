"""Ajuda: localizar os dois builds do Python 3.15 (com GIL e free-threaded) e rodar código neles."""
import subprocess
import sys


def find_python(spec):
    """spec: '3.15' (com GIL) ou '3.15+freethreaded'. Devolve o caminho ou None."""
    result = subprocess.run([sys.executable, "-m", "uv", "python", "find", spec], capture_output=True, text=True)
    return result.stdout.strip() or None


def builds():
    return [("com GIL", find_python("3.15")), ("sem GIL (3.15t)", find_python("3.15+freethreaded"))]


def run_code(python, code, timeout=300):
    result = subprocess.run([python, "-c", code], capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr[-500:])
    return result.stdout.strip()
