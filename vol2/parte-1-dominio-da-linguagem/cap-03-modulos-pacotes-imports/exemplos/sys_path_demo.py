"""sys.path: ordem de busca, PYTHONPATH e arquivos .pth."""
import os
import site
import subprocess
import sys
import tempfile
from pathlib import Path

print("sys.path[0] (pasta do script):", Path(sys.path[0]).name)
for entry in sys.path[1:]:
    print("  ", Path(entry).name)

with tempfile.TemporaryDirectory() as tmp:
    lib = Path(tmp) / "mylibs"
    lib.mkdir()
    (lib / "secret_tool.py").write_text("NAME = 'from PYTHONPATH'\n")

    code = "import secret_tool; print(secret_tool.NAME)"
    env = {**os.environ, "PYTHONPATH": str(lib)}
    out = subprocess.run([sys.executable, "-c", code], env=env,
                         capture_output=True, text=True, cwd=tmp)
    print(out.stdout.strip())
    out = subprocess.run([sys.executable, "-I", "-c", code], env=env,
                         capture_output=True, text=True, cwd=tmp)
    print("-I ignora PYTHONPATH:", out.stderr.strip().splitlines()[-1])

    # Um arquivo .pth em uma pasta "site" adiciona entradas ao sys.path
    site_dir = Path(tmp) / "fake_site"
    site_dir.mkdir()
    (site_dir / "extra.pth").write_text(f"{lib}\n")
    site.addsitedir(str(site_dir))
    print("lib em sys.path via .pth?", str(lib) in sys.path)
    import secret_tool
    print(secret_tool.NAME.replace("PYTHONPATH", ".pth"))
