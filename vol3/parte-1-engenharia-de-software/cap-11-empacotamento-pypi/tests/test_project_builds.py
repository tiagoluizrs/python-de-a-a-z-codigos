"""O projeto empacotado nos exemplos precisa construir e passar no twine check."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_project_builds_and_passes_twine(tmp_path):
    work = tmp_path / "projeto"
    shutil.copytree(ROOT / "projeto", work, ignore=shutil.ignore_patterns("dist", "__pycache__"))
    built = subprocess.run([sys.executable, "-m", "uv", "build", str(work)], capture_output=True, text=True)
    assert built.returncode == 0, built.stderr
    files = sorted((work / "dist").glob("greeter*"))
    assert [f.name for f in files] == ["greeter_demo-0.3.0-py3-none-any.whl", "greeter_demo-0.3.0.tar.gz"]
    check = subprocess.run([sys.executable, "-m", "twine", "check", *map(str, files)], capture_output=True, text=True)
    assert check.returncode == 0 and check.stdout.count("PASSED") == 2, check.stdout + check.stderr
