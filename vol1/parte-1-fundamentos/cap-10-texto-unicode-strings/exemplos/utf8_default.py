"""O que o Python 3.15 muda no padrão de codificação (PEP 686)."""
import locale
import sys
from pathlib import Path

print("utf8_mode:", sys.flags.utf8_mode)
print("locale.getencoding():", locale.getencoding())
print("getpreferredencoding:", locale.getpreferredencoding(False))
print("stdout:", sys.stdout.encoding, "| fs:", sys.getfilesystemencoding())

path = Path("sample_cp1252.txt")
path.write_bytes("ação".encode("cp1252"))          # arquivo "legado"
try:
    print("sem encoding:", path.read_text())
except UnicodeDecodeError as exc:
    print("sem encoding falhou:", exc.reason)
print("encoding='locale':", path.read_text(encoding="locale"))
print("encoding='cp1252':", path.read_text(encoding="cp1252"))

out = Path("sample_default.txt")
out.write_text("ação")                             # escreve com o padrão
print(out.read_bytes())
path.unlink()
out.unlink()
