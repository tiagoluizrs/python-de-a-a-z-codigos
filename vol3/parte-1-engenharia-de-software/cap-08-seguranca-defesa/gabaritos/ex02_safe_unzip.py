"""Gabarito do exercício 2."""
import zipfile
from pathlib import Path


def safe_extract_zip(zip_path, dest, *, max_files=100, max_total_bytes=10_000_000, max_ratio=100):
    root = Path(dest).resolve()
    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        if len(infos) > max_files:
            raise ValueError("arquivos demais")
        total = 0
        targets = []
        for info in infos:
            name = info.filename
            if "\0" in name:
                raise ValueError("byte nulo no nome")
            target = (root / name).resolve()
            if name.startswith(("/", "\\")) or not target.is_relative_to(root) or (len(name) > 1 and name[1] == ":"):
                raise ValueError(f"entrada insegura: {name!r}")
            total += info.file_size
            if info.file_size and (info.compress_size == 0 or info.file_size / info.compress_size > max_ratio):
                raise ValueError(f"razão de compressão suspeita: {name!r}")
            targets.append((info, target))
        if total > max_total_bytes:
            raise ValueError("tamanho total excede o limite")
        extracted = []
        for info, target in targets:
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            written = 0
            with archive.open(info) as source, open(target, "wb") as out:
                while chunk := source.read(65536):
                    written += len(chunk)
                    if written > max_total_bytes:
                        raise ValueError("tamanho real excede o limite")
                    out.write(chunk)
            extracted.append(info.filename)
        return sorted(extracted)
