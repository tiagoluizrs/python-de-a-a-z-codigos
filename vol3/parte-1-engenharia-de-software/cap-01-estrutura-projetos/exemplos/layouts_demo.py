"""Layout plano x layout src: por que o segundo evita enganos."""
import subprocess
import sys
import tempfile
from pathlib import Path


def run(args, cwd):
    result = subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)
    lines = (result.stdout or result.stderr).strip().splitlines()
    return lines[-1] if lines else ""


with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)

    flat = root / "flat"
    (flat / "mylib").mkdir(parents=True)
    (flat / "mylib" / "__init__.py").write_text("VALUE = 1\n")

    src = root / "src_layout"
    (src / "src" / "mylib").mkdir(parents=True)
    (src / "src" / "mylib" / "__init__.py").write_text("VALUE = 1\n")

    print("plano, sem instalar:", run(["-c", "import mylib; print('importou', mylib.VALUE)"], flat))
    print("src,   sem instalar:", run(["-c", "import mylib"], src))
    print("src, com PYTHONPATH=src:", run(["-c", "import sys; sys.path.insert(0, 'src'); import mylib; print('importou', mylib.VALUE)"], src))

    # Por que o plano "funciona": o diretório atual entra no sys.path com -c / -m / pytest antigo
    print("sys.path[0] com -c:", run(["-c", "import sys; print(repr(sys.path[0]))"], flat))
    (flat / "show.py").write_text("import sys; print(sys.path[0] == __import__('os').path.dirname(__file__))\n")
    print("sys.path[0] é a pasta do SCRIPT:", run(["show.py"], flat))
    print("com -I (isolado):", run(["-I", "-c", "import mylib"], flat))
