"""O tempo de partida: o interpretador vazio, e o que cada import acrescenta."""
import re
import statistics
import subprocess
import sys
import time


def run(*args, repeat=7):
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        subprocess.run([sys.executable, *args], capture_output=True)
        times.append(time.perf_counter() - start)
    return min(times) * 1e3


print(f"python -c pass          : {run('-c', 'pass'):6.1f} ms")
print(f"python -S -c pass       : {run('-S', '-c', 'pass'):6.1f} ms   (sem o módulo site)")
print(f"python -I -c pass       : {run('-I', '-c', 'pass'):6.1f} ms   (modo isolado)")
print("tempo de import de módulos da biblioteca padrão (processo novo, ms acima do vazio):")
base = run("-c", "pass")
for module in ("json", "re", "decimal", "typing", "asyncio", "dataclasses", "http.client", "unittest"):
    print(f"  import {module:<12}{run('-c', f'import {module}') - base:6.1f}")

# -X importtime: onde o tempo de import foi
result = subprocess.run([sys.executable, "-X", "importtime", "-c", "import asyncio"], capture_output=True, text=True)
rows = []
for line in result.stderr.splitlines():
    match = re.match(r"import time:\s+(\d+) \|\s+(\d+) \| (\s*)(\S+)", line)
    if match:
        rows.append((int(match.group(2)), match.group(4)))
rows.sort(reverse=True)
print("os 4 imports mais caros (cumulativo, us) dentro de `import asyncio`:", rows[:4])
