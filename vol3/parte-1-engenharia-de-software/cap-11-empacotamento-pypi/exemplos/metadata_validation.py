"""Validar metadados antes de publicar: classificadores, twine check e nomes."""
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

from trove_classifiers import classifiers

PROJECT = Path(__file__).resolve().parent.parent / "projeto"
data = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

print("classificadores válidos?", {c: c in classifiers for c in data["classifiers"]})
print("existem", len(classifiers), "classificadores oficiais; exemplos de versão:", [c for c in classifiers if c.startswith("Programming Language :: Python :: 3.1")][:3])
print("um inventado:", "Programming Language :: Python :: 3.99" in classifiers)

# Nome: normalização (PEP 503) e o que o PyPI considera "o mesmo nome"
def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


for a, b in [("Greeter_Demo", "greeter-demo"), ("greeter.demo", "Greeter-Demo"), ("greeter-demo", "greeterdemo")]:
    print(f"  {a!r} e {b!r} são o mesmo nome? {normalize(a) == normalize(b)}")

# twine check: descrição renderizável e metadados completos
with tempfile.TemporaryDirectory() as folder:
    work = Path(folder) / "projeto"
    shutil.copytree(PROJECT, work, ignore=shutil.ignore_patterns("dist", "__pycache__"))
    subprocess.run([sys.executable, "-m", "uv", "build", str(work)], capture_output=True)
    env = {**__import__("os").environ, "COLUMNS": "300", "NO_COLOR": "1"}
    result = subprocess.run([sys.executable, "-m", "twine", "check", *map(str, (work / "dist").glob("greeter*"))], capture_output=True, text=True, env=env)
    for name, verdict in re.findall(r"(greeter\S+\.(?:whl|tar\.gz)): (PASSED|FAILED)", " ".join(result.stdout.split())):
        print(f"twine check {name}: {verdict}")

    # Uma descrição quebrada: README com reST inválido, declarado como rst
    broken = Path(folder) / "broken"
    shutil.copytree(work, broken, ignore=shutil.ignore_patterns("dist"))
    (broken / "README.rst").write_text("Título\n===\n\n.. code-block::\n  sem linha em branco e com `erro\n", encoding="utf-8")
    text = (broken / "pyproject.toml").read_text(encoding="utf-8").replace('readme = "README.md"', 'readme = "README.rst"')
    (broken / "pyproject.toml").write_text(text, encoding="utf-8")
    shutil.rmtree(broken / "dist", ignore_errors=True)
    subprocess.run([sys.executable, "-m", "uv", "build", str(broken)], capture_output=True)
    result = subprocess.run([sys.executable, "-m", "twine", "check", *map(str, (broken / "dist").glob("*.whl"))], capture_output=True, text=True, env=env)
    text = " ".join((result.stdout + result.stderr).split())
    verdict = re.search(r"(PASSED|FAILED)", text)
    reason = re.search(r"ERROR (.{0,110})", text)
    print("README inválido ->", verdict.group(1) if verdict else "?", "|", reason.group(1) if reason else "")
