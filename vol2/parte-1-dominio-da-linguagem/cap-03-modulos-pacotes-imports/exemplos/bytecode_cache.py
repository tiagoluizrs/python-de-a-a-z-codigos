"""Cache de bytecode: __pycache__, nome do .pyc e invalidacao."""
import importlib.util
import os
import py_compile
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "mod_demo.py"
    src.write_text("VALUE = 1\n", encoding="utf-8")

    pyc = importlib.util.cache_from_source(str(src))
    print(Path(pyc).relative_to(tmp))
    print("tag:", sys.implementation.cache_tag)

    sys.path.insert(0, tmp)
    import mod_demo
    print("existe .pyc?", os.path.exists(pyc))

    head = Path(pyc).read_bytes()[:16]
    print("flags (bytes 4-8):", int.from_bytes(head[4:8], "little"))
    print("mtime gravado == mtime do .py?",
          int.from_bytes(head[8:12], "little") == int(src.stat().st_mtime))

    # Modo por hash: o .pyc guarda o hash do fonte, nao o timestamp
    py_compile.compile(str(src), cfile=pyc,
                       invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH)
    head = Path(pyc).read_bytes()[:16]
    print("flags com hash:", int.from_bytes(head[4:8], "little"))
    sys.path.remove(tmp)
    del sys.modules["mod_demo"]

# Pegadinha: o timestamp guarda mtime (em segundos) e tamanho do fonte.
# Se os dois ficarem iguais, o .pyc velho e usado.
def run_import(folder: str) -> str:
    import subprocess
    out = subprocess.run(
        [sys.executable, "-c", "import stale_demo; print(stale_demo.V)"],
        cwd=folder, capture_output=True, text=True)
    return out.stdout.strip()


with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "stale_demo.py"
    src.write_text("V = 1\n", encoding="utf-8")
    stamp = src.stat().st_mtime_ns
    print("primeira execucao:", run_import(tmp))
    src.write_text("V = 2\n", encoding="utf-8")   # mesmo tamanho
    os.utime(src, ns=(stamp, stamp))               # mesmo mtime
    print("depois de editar :", run_import(tmp))   # ainda 1!
    pyc = importlib.util.cache_from_source(str(src))
    py_compile.compile(str(src), cfile=pyc, invalidation_mode=
                       py_compile.PycInvalidationMode.CHECKED_HASH)
    print("com pyc por hash :", run_import(tmp))

# Importar sem gravar bytecode (-B ou PYTHONDONTWRITEBYTECODE=1)
print("dont_write_bytecode:", sys.dont_write_bytecode)
