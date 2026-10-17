"""Escrita atômica: temporário no mesmo diretório + os.replace."""
import os
import tempfile
from pathlib import Path


def atomic_write_text(path, text, encoding="utf-8"):
    path = Path(path)
    # O temporário precisa estar no MESMO diretório (mesmo volume),
    # senão o replace deixaria de ser uma operação atômica.
    fd, tmp_name = tempfile.mkstemp(dir=path.parent,
                                    prefix=path.name + ".",
                                    suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())          # força a gravação no disco
        os.replace(tmp_name, path)        # troca atômica
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def naive_write_text(path, text, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:   # trunca já!
        f.write(text)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="cap11_") as tmp:
        target = Path(tmp) / "config.txt"
        new = "version: 2 (configuração)"   # não cabe em ASCII

        target.write_text("version: 1", encoding="utf-8")
        try:
            naive_write_text(target, new, encoding="ascii")
        except UnicodeEncodeError:
            pass
        print("ingênuo:", repr(target.read_text(encoding="utf-8")))

        target.write_text("version: 1", encoding="utf-8")
        try:
            atomic_write_text(target, new, encoding="ascii")
        except UnicodeEncodeError:
            pass
        print("atômico:", repr(target.read_text(encoding="utf-8")))
        print(sorted(p.name for p in Path(tmp).iterdir()))

        atomic_write_text(target, new)
        print("sucesso:", repr(target.read_text(encoding="utf-8")))
