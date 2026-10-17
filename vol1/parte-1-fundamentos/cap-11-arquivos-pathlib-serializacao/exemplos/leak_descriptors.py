"""O que acontece quando arquivos não são fechados."""
import shutil
import tempfile
from pathlib import Path

workdir = Path(tempfile.mkdtemp(prefix="cap11_"))
target = workdir / "data.txt"
target.write_text("x", encoding="utf-8")

# Guardar as referências impede o coletor de fechar os arquivos.
handles = []
try:
    for i in range(100_000):
        handles.append(open(target, encoding="utf-8"))
except OSError as exc:
    print(f"falhou com {len(handles)} arquivos abertos")
    print(type(exc).__name__, exc.errno, exc.strerror)
finally:
    for handle in handles:
        handle.close()
    shutil.rmtree(workdir)
