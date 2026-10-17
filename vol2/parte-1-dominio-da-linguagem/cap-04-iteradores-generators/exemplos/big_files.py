"""Iterar fluxos grandes: arquivo, blocos e CSV com memoria constante."""
import csv
import tempfile
import tracemalloc
from itertools import islice
from pathlib import Path


def read_in_chunks(handle, size=8192):
    while chunk := handle.read(size):
        yield chunk


def lines_with_errors(path):
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if "ERROR" in line:
                yield line.rstrip("\n")


with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "big.log"
    with open(path, "w", encoding="utf-8") as out:
        for i in range(500_000):
            level = "ERROR" if i % 1000 == 0 else "INFO"
            out.write(f"2026-01-01 00:00:{i % 60:02d} {level} msg {i}\n")
    print(f"arquivo: {path.stat().st_size / 1e6:.1f} MB")

    tracemalloc.start()
    count = sum(1 for _ in lines_with_errors(path))
    peak_gen = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    tracemalloc.start()
    all_lines = path.read_text(encoding="utf-8").splitlines()
    count_list = sum(1 for line in all_lines if "ERROR" in line)
    peak_list = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    del all_lines
    print(count, count_list)
    print(f"gerador: {peak_gen / 1e3:.1f} KB | lista: "
          f"{peak_list / 1e6:.1f} MB")

    with open(path, "rb") as handle:
        sizes = [len(c) for c in islice(read_in_chunks(handle, 1_000_000), 3)]
    print(sizes)
