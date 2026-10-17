"""Sombreamento: um random.py no projeto quebra tudo."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent / "shadow_demo"

out = subprocess.run([sys.executable, "main.py"], cwd=HERE,
                     capture_output=True, text=True)
print("\n".join(out.stderr.strip().splitlines()[-2:]))

# Defesas
print("random" in sys.stdlib_module_names)
print(len(sys.stdlib_module_names) > 200)

# -P (ou PYTHONSAFEPATH) nao poe a pasta do script no sys.path...
out = subprocess.run([sys.executable, "-P", "main.py"], cwd=HERE,
                     capture_output=True, text=True)
print("com -P:", out.stdout.split()[0])   # random.py da stdlib

# ...e -I (modo isolado) tambem ignora PYTHONPATH e site do usuario
