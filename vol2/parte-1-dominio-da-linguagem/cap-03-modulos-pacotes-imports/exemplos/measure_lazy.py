"""Import normal x lazy import: tempo total de um processo."""
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HEAVY = ["asyncio", "http.client", "email.message", "sqlite3",
         "decimal", "argparse"]

BODY = '''
import sys
if len(sys.argv) > 1:      # caminho raro: so ele usa os modulos
    print(asyncio.__name__, sqlite3.__name__)
print("done")
'''


def make_script(folder: Path, name: str, prefix: str) -> Path:
    header = "\n".join(f"{prefix}import {m}" for m in HEAVY)
    path = folder / name
    path.write_text(header + BODY, encoding="utf-8")
    return path


def median_ms(args: list[str], runs: int = 30) -> float:
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        subprocess.run(args, capture_output=True, check=True)
        times.append((time.perf_counter() - start) * 1000)
    return statistics.median(times)


with tempfile.TemporaryDirectory() as tmp:
    folder = Path(tmp)
    eager = make_script(folder, "eager.py", "")
    lazy = make_script(folder, "lazy.py", "lazy ")
    py = sys.executable
    print(f"interpretador vazio : {median_ms([py, '-c', 'pass']):6.1f} ms")
    print(f"import normal       : {median_ms([py, str(eager)]):6.1f} ms")
    print(f"lazy import         : {median_ms([py, str(lazy)]):6.1f} ms")
    print(f"lazy, caminho raro  : {median_ms([py, str(lazy), 'x']):6.1f} ms")
    print(f"-X lazy_imports=all : "
          f"{median_ms([py, '-X', 'lazy_imports=all', str(eager)]):6.1f} ms")
