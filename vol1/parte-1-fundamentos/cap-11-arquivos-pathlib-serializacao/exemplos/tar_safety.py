"""tarfile: um membro malicioso tentando escapar do destino."""
import io
import tarfile
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="cap11_") as tmp:
    root = Path(tmp)
    with tarfile.open(root / "bad.tar", "w") as tf:
        info = tarfile.TarInfo("../evil.txt")   # sobe um diretório
        info.size = 1
        tf.addfile(info, io.BytesIO(b"x"))

    out = root / "out"
    out.mkdir()
    for kwargs in ({}, {"filter": "fully_trusted"}):
        try:
            with tarfile.open(root / "bad.tar") as tf:
                tf.extractall(out, **kwargs)
            print(kwargs, "-> extraiu fora?", (root / "evil.txt").exists())
        except tarfile.OutsideDestinationError:
            print(kwargs, "-> OutsideDestinationError")
