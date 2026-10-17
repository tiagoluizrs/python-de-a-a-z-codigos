"""Path traversal e zip/tar slip: nomes vindos de fora não podem sair da pasta-base."""
import io
import os
import tarfile
import tempfile
import zipfile
from pathlib import Path

base = Path(tempfile.mkdtemp()).resolve()

# O operador / descarta a base quando o segundo operando é absoluto
print("base / '/etc/passwd'      ->", Path("/srv/files") / "/etc/passwd")
print("base / '../../etc/passwd' ->", (Path("/srv/files") / "../../etc/passwd").as_posix(), "(sem resolver, ainda parece dentro)")


def unsafe_join(name):
    return base / name


def safe_join(name):
    resolved = (base / name).resolve()
    if not resolved.is_relative_to(base):
        raise ValueError(f"fora da pasta-base: {name!r}")
    return resolved


for name in ("relatorio.txt", "../segredo.txt", "sub/../../fora.txt"):
    unsafe = unsafe_join(name).resolve()
    try:
        safe_join(name)
        verdict = "ok"
    except ValueError as error:
        verdict = f"RECUSADO ({error})"
    print(f"{name:<20} inseguro sai da base: {not unsafe.is_relative_to(base)!s:<5} | seguro: {verdict[:40]}")

# Nome absoluto: no Windows, uma unidade (C:\x) também
absolute = "C:/Windows/system.ini" if os.name == "nt" else "/etc/passwd"
print("absoluto escapa da base?", not (base / absolute).resolve().is_relative_to(base))

# --- Zip slip: entradas com .. dentro de um arquivo compactado -------------------------------------------
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w") as archive:
    archive.writestr("../zipslip.txt", "x")
    archive.writestr("a/ok.txt", "z")
buffer.seek(0)
with zipfile.ZipFile(buffer) as archive:
    names = [info.filename for info in archive.infolist()]
    dest = base / "zip_dest"
    archive.extractall(dest)                                    # extractall do zipfile SANEIA os nomes
print("nomes no zip:", names, "| extraído:", sorted(p.relative_to(base).as_posix() for p in base.rglob("*.txt")))

# Um extrator MANUAL (open(dest / info.filename)) herdaria o problema: confira sempre
for info_name in names:
    target = (dest / info_name).resolve()
    print(f"  manual: {info_name:<16} -> {'DENTRO' if target.is_relative_to(dest.resolve()) else 'FORA da pasta de destino'}")

# --- Tar: o filtro 'data' (padrão desde o 3.14) recusa o que escapa -----------------------------------------
buffer = io.BytesIO()
with tarfile.open(fileobj=buffer, mode="w") as archive:
    info = tarfile.TarInfo("../evil.txt")
    info.size = 3
    archive.addfile(info, io.BytesIO(b"bad"))
buffer.seek(0)
with tarfile.open(fileobj=buffer) as archive:
    try:
        archive.extractall(base / "tar_dest")
    except tarfile.OutsideDestinationError as error:
        print("tar (filtro padrão):", type(error).__name__)
