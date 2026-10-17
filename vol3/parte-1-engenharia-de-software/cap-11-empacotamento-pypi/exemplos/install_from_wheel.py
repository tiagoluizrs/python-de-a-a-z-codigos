"""Instalar a wheel em um ambiente NOVO e usar o pacote como um usuário usaria."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent / "projeto"
uv = [sys.executable, "-m", "uv"]


def run(*args, **kwargs):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", **kwargs)


with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    work = folder / "projeto"
    shutil.copytree(PROJECT, work, ignore=shutil.ignore_patterns("dist", "__pycache__"))
    run(*uv, "build", str(work))
    wheel = next((work / "dist").glob("*.whl"))

    venv = folder / "venv"
    run(*uv, "venv", str(venv), "--python", sys.executable)
    python = venv / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
    result = run(*uv, "pip", "install", "--python", str(python), str(wheel))
    installed = [line.strip() for line in result.stderr.splitlines() if line.strip().startswith("+")]
    print("instalado:", installed)

    out = run(str(python), "-c", "import greeter; print(greeter.greeting('Ana'))")
    print("import + arquivo de dados do pacote:", out.stdout.strip())
    script = venv / ("Scripts" if sys.platform == "win32" else "bin") / ("greeter.exe" if sys.platform == "win32" else "greeter")
    print("comando de console criado:", script.exists(), "|", run(str(script), "Bia").stdout.strip())
    meta = run(str(python), "-c", "import importlib.metadata as m; d = m.distribution('greeter-demo'); print(d.version, d.requires, d.metadata['Requires-Python'])")
    print("metadados no ambiente:", meta.stdout.strip())
    typed = run(str(python), "-c", "import greeter, pathlib; print((pathlib.Path(greeter.__file__).parent / 'py.typed').exists())")
    print("py.typed instalado (o pacote declara tipos):", typed.stdout.strip())
