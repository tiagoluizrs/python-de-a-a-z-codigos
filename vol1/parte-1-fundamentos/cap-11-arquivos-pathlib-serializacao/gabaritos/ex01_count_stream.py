"""Gabarito do exercício 1."""
from pathlib import Path


def count_stream(path: Path) -> tuple[int, int, int]:
    lines = words = chars = 0
    # newline="" mantém \r\n intactos, então len(line) conta tudo.
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:              # um buffer, uma linha por vez
            lines += 1
            words += len(line.split())
            chars += len(line)
    return lines, words, chars
