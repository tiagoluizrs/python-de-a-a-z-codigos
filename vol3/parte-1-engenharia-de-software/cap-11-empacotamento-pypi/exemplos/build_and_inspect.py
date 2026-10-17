"""Construir um projeto e abrir os artefatos: wheel, sdist, METADATA, RECORD."""
import base64
import hashlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent / "projeto"

with tempfile.TemporaryDirectory() as folder:
    work = Path(folder) / "projeto"
    shutil.copytree(PROJECT, work, ignore=shutil.ignore_patterns("dist", "__pycache__"))
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "-m", "uv", "build", str(work)], capture_output=True, text=True, encoding="utf-8")
    elapsed = time.perf_counter() - start
    dist = work / "dist"
    print(f"uv build: {elapsed:.1f} s | artefatos:", sorted(p.name for p in dist.iterdir() if p.name != ".gitignore"))
    wheel = next(dist.glob("*.whl"))
    sdist = next(dist.glob("*.tar.gz"))
    print(f"tamanhos: wheel {wheel.stat().st_size} bytes | sdist {sdist.stat().st_size} bytes")

    with zipfile.ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        print("\nconteúdo da wheel:")
        for name in names:
            print("  ", name)
        metadata = archive.read("greeter_demo-0.3.0.dist-info/METADATA").decode()
        print("\nMETADATA (campos principais):")
        for line in metadata.splitlines():
            if line.split(":")[0] in ("Name", "Version", "Requires-Dist", "Requires-Python", "License-Expression", "Provides-Extra", "Project-URL"):
                print("  ", line)
        print("\nWHEEL:", archive.read("greeter_demo-0.3.0.dist-info/WHEEL").decode().replace("\n", " | "))
        print("entry_points.txt:", archive.read("greeter_demo-0.3.0.dist-info/entry_points.txt").decode().strip().replace("\n", " | "))

        # RECORD: o hash de cada arquivo, para a verificação na instalação
        record = archive.read("greeter_demo-0.3.0.dist-info/RECORD").decode().strip().splitlines()
        bad = []
        for line in record:
            path, digest, size = line.split(",")
            if not digest:
                continue                                                  # o próprio RECORD
            data = archive.read(path)
            expected = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
            if expected != digest or len(data) != int(size):
                bad.append(path)
        print(f"\nRECORD: {len(record)} linhas; arquivos com hash divergente: {bad}")

    with tarfile.open(sdist) as archive:
        print("\nconteúdo da sdist:")
        for member in archive.getmembers():
            if member.isfile():
                print("  ", member.name)
    print("\no que NÃO está na wheel:", [p for p in ("tests", "docs", "README.md") if not any(n.startswith(p) for n in names)])
