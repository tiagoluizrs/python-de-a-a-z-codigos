"""Gabarito do exercício 3."""
import os
import tempfile
from pathlib import Path


def safe_write(path: Path, data: str | bytes) -> None:
    path = Path(path)
    if isinstance(data, str):
        payload = data.encode("utf-8")
    elif isinstance(data, bytes):
        payload = data
    else:
        # Falha ANTES de criar qualquer arquivo temporário.
        raise TypeError(f"expected str or bytes, got {type(data).__name__}")

    # Mesmo diretório = mesmo volume: só assim os.replace é atômico.
    fd, tmp_name = tempfile.mkstemp(dir=path.parent,
                                    prefix=f".{path.name}.",
                                    suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())    # garante que chegou ao disco
        os.replace(tmp_name, path)  # troca atômica pelo nome final
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
