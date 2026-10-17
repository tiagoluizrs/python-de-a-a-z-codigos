"""gzip, zipfile, tarfile e compression.zstd (3.14+)."""
import gzip
import tarfile
import tempfile
import time
import zipfile
from compression import zstd
from pathlib import Path

text = "".join(
    f"ts=2026-10-12T09:{i // 60 % 60:02d}:{i % 60:02d} level=INFO "
    f"user={i * 7919 % 1000} latency={i * 37 % 500}ms\n"
    for i in range(20000))
raw = text.encode("utf-8")
print("original:", len(raw), "bytes")


def timed(label, func):
    start = time.perf_counter()
    out = func(raw)
    ms = (time.perf_counter() - start) * 1000
    print(f"{label:10} {len(out):8} bytes  {ms:6.1f} ms")
    return out


gz = timed("gzip", gzip.compress)
zs = timed("zstd", zstd.compress)
assert gzip.decompress(gz) == raw and zstd.decompress(zs) == raw

with tempfile.TemporaryDirectory(prefix="cap11_") as tmp:
    root = Path(tmp)
    (root / "src").mkdir()
    (root / "src" / "a.txt").write_text(text[:200], encoding="utf-8")
    (root / "src" / "b.txt").write_text("hello\n", encoding="utf-8")

    # --- gzip: um fluxo único, abre como arquivo (texto ou binário)
    with gzip.open(root / "log.txt.gz", "wt", encoding="utf-8") as f:
        f.write(text)
    with gzip.open(root / "log.txt.gz", "rt", encoding="utf-8") as f:
        print(sum(1 for _ in f), "linhas lidas em streaming")

    # --- zipfile: vários arquivos, acesso aleatório por nome
    with zipfile.ZipFile(root / "pack.zip", "w",
                         compression=zipfile.ZIP_DEFLATED) as zf:
        for p in (root / "src").iterdir():
            zf.write(p, arcname=p.name)
    with zipfile.ZipFile(root / "pack.zip") as zf:
        print(zf.namelist())
        print(zf.read("b.txt"))

    # --- tarfile: vários arquivos em fluxo; compressão por extensão
    with tarfile.open(root / "pack.tar.gz", "w:gz") as tf:
        tf.add(root / "src", arcname="src")
    with tarfile.open(root / "pack.tar.gz") as tf:
        print(tf.getnames())
        tf.extractall(root / "out", filter="data")   # sempre filtre
    print(sorted(p.name for p in (root / "out" / "src").iterdir()))

    # --- zstd com a API de arquivo
    with zstd.open(root / "log.zst", "wb") as f:
        f.write(raw)
    print((root / "log.zst").stat().st_size, "bytes em log.zst")
