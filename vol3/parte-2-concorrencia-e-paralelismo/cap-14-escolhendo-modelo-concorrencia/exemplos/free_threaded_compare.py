"""A mesma carga de CPU com threads: build com GIL x build sem GIL (3.15t)."""
import json
import subprocess
import sys

CODE = """
import json, sys, sysconfig, time
import concurrent.futures as cf

def cpu(n=1_500_000):
    t = 0
    for i in range(n):
        t += i * i % 7
    return t

def run(workers, items=16):
    start = time.perf_counter()
    with cf.ThreadPoolExecutor(workers) as pool:
        list(pool.map(lambda _: cpu(), range(items)))
    return time.perf_counter() - start

seq = run(1)
par = run(16)
print(json.dumps({"gil": sys._is_gil_enabled(), "build": bool(sysconfig.get_config_var("Py_GIL_DISABLED")), "seq": seq, "par": par}))
"""


def find_free_threaded():
    result = subprocess.run([sys.executable, "-m", "uv", "python", "find", "3.15+freethreaded"], capture_output=True, text=True)
    path = result.stdout.strip()
    return path or None


if __name__ == "__main__":
    for label, python in [("build com GIL", sys.executable), ("build sem GIL (3.15t)", find_free_threaded())]:
        if not python:
            print(f"{label}: não instalado (uv python install 3.15+freethreaded)")
            continue
        out = subprocess.run([python, "-c", CODE], capture_output=True, text=True)
        try:
            data = json.loads(out.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            print(label, "falhou:", out.stderr[-200:])
            continue
        print(f"{label:<24} GIL ativo: {data['gil']!s:<5} | 16 tarefas em 1 thread: {data['seq']:.2f} s | em 16 threads: {data['par']:.2f} s | "
              f"ganho: {data['seq'] / data['par']:.1f}x")
