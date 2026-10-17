"""Verificar o que seria enviado, SEM enviar nada."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent / "projeto"
with tempfile.TemporaryDirectory() as folder:
    work = Path(folder) / "projeto"
    shutil.copytree(PROJECT, work, ignore=shutil.ignore_patterns("dist", "__pycache__"))
    subprocess.run([sys.executable, "-m", "uv", "build", str(work)], capture_output=True)
    files = [str(p) for p in (work / "dist").glob("greeter*")]
    result = subprocess.run([sys.executable, "-m", "uv", "publish", "--dry-run", "--publish-url", "https://test.pypi.org/legacy/", *files],
                            capture_output=True, text=True, encoding="utf-8")
    for line in (result.stdout + result.stderr).splitlines():
        if line.startswith(("Checking", "Note:", "error")) and "Trusted publishing" not in line:
            print(line.replace(str(work / "dist") + chr(92), "")[:130])
print("nada foi enviado: --dry-run só confere os arquivos")
