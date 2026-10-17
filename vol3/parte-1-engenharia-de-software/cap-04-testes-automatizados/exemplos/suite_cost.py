"""Quanto custa uma suíte: coleta, execução e o efeito de -p no:cacheprovider."""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    for n in range(10):
        body = "\n".join(f"def test_{n}_{i}():\n    assert {i} + 1 == {i + 1}\n" for i in range(100))
        (root / f"test_gen_{n}.py").write_text(body, encoding="utf-8")
    cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", "--rootdir", folder, str(root)]
    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    elapsed = time.perf_counter() - start
    print(result.stdout.strip().splitlines()[-1])
    print(f"tempo total (processo inteiro): {elapsed:.2f} s")
    start = time.perf_counter()
    subprocess.run([sys.executable, "-m", "pytest", "--version"], capture_output=True)
    print(f"só iniciar o pytest: {time.perf_counter() - start:.2f} s")
