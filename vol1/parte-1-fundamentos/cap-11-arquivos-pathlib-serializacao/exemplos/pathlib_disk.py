"""pathlib tocando o disco: criar, ler, listar, buscar, mover."""
import shutil
import tempfile
from pathlib import Path

root = Path(tempfile.mkdtemp(prefix="cap11_"))

# --- criar diretórios e arquivos
(root / "src" / "pkg").mkdir(parents=True)
(root / "src" / "pkg").mkdir(parents=True, exist_ok=True)  # sem erro
(root / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
(root / "src" / "pkg" / "util.py").write_text("X = 1\n", encoding="utf-8")
(root / "src" / "pkg" / "data.bin").write_bytes(b"\x00\x01\x02")
(root / "README.md").write_text("# demo\n", encoding="utf-8")

# --- consultar
readme = root / "README.md"
print(readme.exists(), readme.is_file(), readme.is_dir())
print(readme.stat().st_size, "bytes")
print(readme.read_text(encoding="utf-8").strip())
print(readme.read_bytes())

# --- listar: iterdir é um nível, sem ordem garantida
print(sorted(p.name for p in root.iterdir()))

# --- glob (um nível ou padrão) e rglob (recursivo)
print(sorted(p.relative_to(root).as_posix() for p in root.glob("src/*.py")))
print(sorted(p.relative_to(root).as_posix() for p in root.rglob("*.py")))

# --- walk (3.12): como os.walk, mas com Path
for dirpath, dirnames, filenames in root.walk():
    print(dirpath.relative_to(root).as_posix() or ".",
          sorted(dirnames), sorted(filenames))

# --- renomear e substituir
old = root / "README.md"
new = old.rename(root / "LEIAME.md")
print(new.name, old.exists())

# --- copiar e mover (3.14)
copy = new.copy(root / "copy.md")
print(copy.name, copy.read_text(encoding="utf-8").strip())
moved = copy.move(root / "src" / "copy.md")
print(moved.relative_to(root).as_posix(), copy.exists())
backup = (root / "src").copy(root / "src_backup")   # árvore inteira
print(sorted(p.relative_to(backup).as_posix() for p in backup.rglob("*")))

# --- apagar
moved.unlink()
moved.unlink(missing_ok=True)       # não levanta erro
shutil.rmtree(root / "src_backup")
try:
    (root / "src").rmdir()          # só apaga diretório vazio
except OSError as exc:
    print(type(exc).__name__)

# --- erros comuns
try:
    (root / "nope" / "file.txt").write_text("x", encoding="utf-8")
except FileNotFoundError as exc:
    print("FileNotFoundError:", exc.filename.endswith("file.txt"))

shutil.rmtree(root)
