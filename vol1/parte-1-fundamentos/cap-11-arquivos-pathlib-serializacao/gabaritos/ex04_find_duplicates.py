"""Gabarito do exercício 4."""
import hashlib
from collections import defaultdict
from pathlib import Path

BLOCK = 64 * 1024


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(BLOCK):   # memória constante
            digest.update(block)
    return digest.hexdigest()


def find_duplicates(root: Path) -> list[list[Path]]:
    # 1) tamanho: arquivos de tamanhos diferentes nunca são iguais
    by_size = defaultdict(list)
    for path in Path(root).rglob("*"):
        if path.is_file():
            by_size[path.stat().st_size].append(path)

    # 2) hash só dos candidatos
    by_hash = defaultdict(list)
    for size, candidates in by_size.items():
        if len(candidates) < 2:
            continue
        for path in candidates:
            by_hash[(size, file_digest(path))].append(path)

    groups = [sorted(g) for g in by_hash.values() if len(g) > 1]
    return sorted(groups, key=lambda g: g[0])
