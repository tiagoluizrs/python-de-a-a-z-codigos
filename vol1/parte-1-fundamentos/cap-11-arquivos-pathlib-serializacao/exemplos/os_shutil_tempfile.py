"""os, shutil e tempfile: o essencial."""
import os
import shutil
import sys
import tempfile
from pathlib import Path

# --- os: ambiente e informações do processo
print(os.getcwd() == str(Path.cwd()))
print(os.name, sys.platform)
print(os.sep, repr(os.linesep), os.pathsep)
print(os.cpu_count() >= 1)
print("PATH" in os.environ or "Path" in os.environ)
print(os.environ.get("CAP11_UNSET", "default"))

# --- shutil: copiar, mover, remover, espaço em disco, which
with tempfile.TemporaryDirectory(prefix="cap11_") as tmp:
    root = Path(tmp)
    src = root / "a.txt"
    src.write_text("hello\n", encoding="utf-8", newline="\n")

    shutil.copy(src, root / "b.txt")      # conteúdo + permissões
    shutil.copy2(src, root / "c.txt")     # + datas (metadados)
    shutil.copytree(root, root / "tree")  # árvore inteira
    print(sorted(p.name for p in (root / "tree").iterdir()))

    shutil.move(root / "b.txt", root / "tree" / "b.txt")
    shutil.rmtree(root / "tree")          # apaga árvore inteira
    print(sorted(p.name for p in root.iterdir()))

    usage = shutil.disk_usage(root)
    print(usage.total > usage.used >= 0, usage.free > 0)

print(shutil.which("python") is not None)
print(shutil.which("definitely-not-a-program"))

# --- tempfile: arquivos e diretórios temporários
with tempfile.TemporaryDirectory(prefix="demo_") as tmp:
    print(Path(tmp).exists())
print(Path(tmp).exists())                 # apagado ao sair

with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", encoding="utf-8", delete=False) as tf:
    tf.write("temp data")
    name = tf.name
print(Path(name).read_text(encoding="utf-8"))
os.unlink(name)

# mkstemp: devolve (descritor, caminho); criado com permissão 0600
fd, name = tempfile.mkstemp(suffix=".bin")
with os.fdopen(fd, "wb") as f:
    f.write(b"\x00\x01")
print(Path(name).stat().st_size)
os.unlink(name)

print(Path(tempfile.gettempdir()).is_dir())
