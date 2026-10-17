"""O mesmo projeto, três backends de construção: o que muda."""
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent / "projeto"
BASE = (PROJECT / "pyproject.toml").read_text(encoding="utf-8")
BASE = re.sub(r"\[build-system\].*?(?=\n\[|\Z)", "", BASE, flags=re.S)
BASE = re.sub(r"\[tool\.uv\.build-backend\].*", "", BASE, flags=re.S).rstrip() + "\n"

CONFIGS = {
    "uv_build": (BASE + '\n[build-system]\nrequires = ["uv_build>=0.13.0,<0.14.0"]\nbuild-backend = "uv_build"\n\n[tool.uv.build-backend]\nmodule-name = "greeter"\n'),
    "hatchling": (BASE + '\n[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n\n[tool.hatch.build.targets.wheel]\npackages = ["src/greeter"]\n'),
    "setuptools": (BASE + '\n[build-system]\nrequires = ["setuptools>=77"]\nbuild-backend = "setuptools.build_meta"\n\n[tool.setuptools.packages.find]\nwhere = ["src"]\n\n[tool.setuptools.package-data]\ngreeter = ["data/*.txt", "py.typed"]\n'),
}

wheel_files = {}
print(f"{'backend':<12}{'tempo':>8}{'wheel (B)':>11}{'sdist (B)':>11}  sdist inclui tests/ e docs/?")
for name, config in CONFIGS.items():
    with tempfile.TemporaryDirectory() as folder:
        work = Path(folder) / "projeto"
        shutil.copytree(PROJECT, work, ignore=shutil.ignore_patterns("dist", "__pycache__"))
        (work / "pyproject.toml").write_text(config, encoding="utf-8")
        start = time.perf_counter()
        subprocess.run([sys.executable, "-m", "uv", "build", str(work)], capture_output=True)
        elapsed = time.perf_counter() - start
        wheel = next((work / "dist").glob("*.whl"))
        sdist = next((work / "dist").glob("*.tar.gz"))
        with zipfile.ZipFile(wheel) as archive:
            wheel_files[name] = sorted(n for n in archive.namelist() if not n.endswith("/") and "dist-info" not in n)
        with tarfile.open(sdist) as archive:
            members = [m.name for m in archive.getmembers()]
        has = [p for p in ("tests/", "docs/") if any(p in m for m in members)]
        print(f"{name:<12}{elapsed:>7.1f}s{wheel.stat().st_size:>11}{sdist.stat().st_size:>11}  {has or 'não'}")

print("o conteúdo (fora de dist-info) das wheels é o mesmo nos três?", len({tuple(v) for v in wheel_files.values()}) == 1, wheel_files["uv_build"])
