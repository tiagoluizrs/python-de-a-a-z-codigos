"""Ler tudo de uma vez x linha a linha x em blocos: memória e tempo."""
import shutil
import tempfile
import time
import tracemalloc
from pathlib import Path

N_LINES = 1_000_000


def count_read_all(path):
    with open(path, encoding="utf-8") as f:
        return len(f.read().splitlines())


def count_readlines(path):
    with open(path, encoding="utf-8") as f:
        return len(f.readlines())


def count_iter(path):
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in f)


def count_blocks(path, size=1 << 20):
    total = 0
    with open(path, "rb") as f:
        while chunk := f.read(size):
            total += chunk.count(b"\n")
    return total


def measure(func, path):
    start = time.perf_counter()
    result = func(path)
    elapsed = time.perf_counter() - start
    tracemalloc.start()
    func(path)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return result, elapsed, peak


def main():
    workdir = Path(tempfile.mkdtemp(prefix="cap11_"))
    path = workdir / "big.txt"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for i in range(N_LINES):
            f.write(f"line {i:07d} with some payload text\n")
    size_mb = path.stat().st_size / 1e6
    print(f"arquivo: {size_mb:.1f} MB, {N_LINES:,} linhas")

    for func in (count_read_all, count_readlines, count_iter,
                 count_blocks):
        result, elapsed, peak = measure(func, path)
        print(f"{func.__name__:16} {result:>9,} "
              f"{elapsed * 1000:7.0f} ms  pico {peak / 1e6:8.2f} MB")
    shutil.rmtree(workdir)


if __name__ == "__main__":
    main()
