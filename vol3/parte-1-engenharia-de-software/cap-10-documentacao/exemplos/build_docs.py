"""Gerar a documentação: Sphinx (completo) e pdoc (simples), com tempos."""
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

with tempfile.TemporaryDirectory() as folder:
    out = Path(folder) / "sphinx"
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "-m", "sphinx", "-b", "html", "-q", "-E", "-d", str(Path(folder) / "doctrees"),
                             str(ROOT / "docs"), str(out)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    elapsed = time.perf_counter() - start
    pages = sorted(p.name for p in out.glob("*.html"))
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    warnings = len([line for line in result.stderr.splitlines() if "WARNING" in line])
    print(f"sphinx: {elapsed:.1f} s | páginas: {pages} | {size / 1e3:.0f} KB | avisos: {warnings} | código {result.returncode}")
    api = (out / "api.html").read_text(encoding="utf-8")
    print("a API foi extraída das docstrings:", all(name in api for name in ("Circle", "Rectangle", "total_area", "largest")),
          "| mostra o argumento radius:", "radius" in api)
    print("trecho do exemplo que o Sphinx renderizou a partir da docstring:", "12.566370614359172" in api)

    out2 = Path(folder) / "pdoc"
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "-m", "pdoc", "shapes", "-o", str(out2)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    elapsed = time.perf_counter() - start
    files = sorted(p.relative_to(out2).as_posix() for p in out2.rglob("*.html"))
    print(f"pdoc: {elapsed:.1f} s | arquivos: {files} | código {result.returncode}")
