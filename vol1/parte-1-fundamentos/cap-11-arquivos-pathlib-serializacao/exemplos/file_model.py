"""O modelo de arquivo: descritor, buffer e ponteiro de posição."""
import io
import os
import shutil
import tempfile
from pathlib import Path

workdir = Path(tempfile.mkdtemp(prefix="cap11_"))
path = workdir / "notes.txt"

# --- camadas: texto -> buffer -> cru -> descritor do SO
f = open(path, "w", encoding="utf-8")
print(type(f).__name__)             # TextIOWrapper
print(type(f.buffer).__name__)      # BufferedWriter
print(type(f.buffer.raw).__name__)  # FileIO
print(f.fileno() > 2)               # 0, 1 e 2: stdin, stdout, stderr
print(io.DEFAULT_BUFFER_SIZE)
f.close()

# --- sem close/flush, os dados ficam no buffer
w = open(path, "w", encoding="utf-8", newline="\n")
w.write("hello\n")
print(path.stat().st_size)          # 0: nada chegou ao disco
w.flush()
print(path.stat().st_size)          # 6
w.close()

# --- ponteiro de posição
with open(path, "w+", encoding="utf-8", newline="\n") as f:
    f.write("abcdef\nghi\n")
    print(f.tell())                 # 11
    f.seek(0)
    print(f.read(3), f.tell())      # abc 3
    print(repr(f.readline()))       # 'def\n'
    f.seek(0, os.SEEK_END)
    print(f.tell())                 # 11

# --- modo binário: seek livre; texto: só posições devolvidas por tell
with open(path, "rb") as f:
    f.seek(-4, os.SEEK_END)
    print(f.read())                 # b'ghi\n'

# --- erros típicos
try:
    open(path, "x")
except FileExistsError as exc:
    print(type(exc).__name__, exc.errno)

try:
    open(workdir / "missing.txt")
except FileNotFoundError as exc:
    print(type(exc).__name__, exc.errno)

# --- StringIO e BytesIO: arquivos em memória
buf = io.StringIO()
buf.write("line 1\nline 2\n")
buf.seek(0)
print(list(buf))
raw = io.BytesIO(b"\x00\x01\x02\x03")
print(raw.read(2), raw.getvalue())

shutil.rmtree(workdir)
