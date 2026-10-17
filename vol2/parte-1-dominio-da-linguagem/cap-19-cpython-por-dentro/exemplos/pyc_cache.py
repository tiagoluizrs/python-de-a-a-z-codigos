"""Arquivos .pyc: o cache de bytecode."""
import importlib.util
import marshal
import os
import py_compile
import struct
import subprocess
import sys
import tempfile
import time

print(importlib.util.cache_from_source("pacote/modulo.py"))
print(sys.implementation.cache_tag, importlib.util.MAGIC_NUMBER)

with tempfile.TemporaryDirectory() as folder:
    source = os.path.join(folder, "mod.py")
    with open(source, "w") as handle:
        handle.write("VALUE = 41 + 1\n")
    pyc = py_compile.compile(source, cfile=os.path.join(folder, "mod.pyc"))
    data = open(pyc, "rb").read()
    sys.stdout.flush()

    magic, flags, mtime, size = data[:4], *struct.unpack("<III", data[4:16])
    print("magic:", magic == importlib.util.MAGIC_NUMBER, "| flags:", flags, "| mtime == fonte:",
          mtime == int(os.stat(source).st_mtime), "| tamanho do fonte:", size)
    code = marshal.loads(data[16:])                   # o resto é o objeto de código serializado
    print(type(code).__name__, code.co_consts)

    # Executar o .pyc direto
    namespace = {}
    exec(code, namespace)
    print(namespace["VALUE"])

    # Efeito no import: o __pycache__ é criado na primeira importação
    pkg = os.path.join(folder, "pk")
    os.mkdir(pkg)
    with open(os.path.join(pkg, "lib.py"), "w") as handle:
        handle.write("X = 1\n")
    cache_dir = os.path.join(pkg, "__pycache__")
    sys.stdout.flush()
    snippet = f"import sys; sys.path.insert(0, {folder!r}); import pk.lib"
    subprocess.run([sys.executable, "-B", "-c", snippet], check=True)       # -B: não escreve .pyc
    print("com -B:", os.path.isdir(cache_dir))
    subprocess.run([sys.executable, "-c", snippet], check=True)
    print("sem -B:", os.listdir(cache_dir))

    # Invalidação: o .pyc guarda mtime e tamanho do fonte; mudou, recompila
    with open(os.path.join(pkg, "lib.py"), "w") as handle:
        handle.write("X = 2222\n")
    sys.stdout.flush()
    subprocess.run([sys.executable, "-c", snippet + "; print('X =', pk.lib.X)"], check=True)
