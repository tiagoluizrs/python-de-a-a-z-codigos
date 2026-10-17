"""Quebras de linha: o que o modo texto faz por você (e contra você)."""
import tempfile
from pathlib import Path

workdir = Path(tempfile.mkdtemp(prefix="cap11_"))
path = workdir / "nl.txt"

# newline=None (padrão): "\n" vira os.linesep ao escrever
with open(path, "w", encoding="utf-8") as f:
    f.write("a\nb\n")
print(path.read_bytes())           # Windows: b'a\r\nb\r\n'

# newline="\n": nenhuma tradução ao escrever
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write("a\nb\n")
print(path.read_bytes())           # b'a\nb\n'

# na leitura, \r\n, \r e \n viram \n (universal newlines)
path.write_bytes(b"x\r\ny\rz\n")
with open(path, encoding="utf-8") as f:
    print(f.readlines())           # ['x\n', 'y\n', 'z\n']

# newline="": nada é traduzido e as terminações originais ficam
with open(path, encoding="utf-8", newline="") as f:
    print(f.readlines())           # ['x\r\n', 'y\r', 'z\n']

import shutil
shutil.rmtree(workdir)
