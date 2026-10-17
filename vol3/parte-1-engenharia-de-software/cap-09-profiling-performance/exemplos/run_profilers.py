"""cProfile (determinístico) x amostragem (3.15): o que cada um mostra e quanto custa."""
import cProfile
import io
import pstats
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent


def seconds(command):
    start = time.perf_counter()
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    return time.perf_counter() - start, result.stdout + result.stderr


# --- cProfile pela API: cada chamada é registrada ---------------------------------------------------------------
sys.path.insert(0, str(HERE))
import workload

profiler = cProfile.Profile()
profiler.enable()
workload.main()
profiler.disable()

stats = pstats.Stats(profiler, stream=io.StringIO())
rows = sorted(stats.stats.items(), key=lambda item: item[1][2], reverse=True)[:6]
print(f"{'ncalls':>8} {'tottime':>8} {'cumtime':>8}  função")
for (filename, lineno, name), (cc, nc, tt, ct, callers) in rows:
    where = f"{Path(filename).name}:{lineno}({name})" if not filename.startswith("~") else name
    print(f"{nc:>8} {tt:>8.3f} {ct:>8.3f}  {where}")

# --- Quem chama quem (print_callers) --------------------------------------------------------------------------------------
buffer = io.StringIO()
pstats.Stats(profiler, stream=buffer).print_callers("append")
print([line.strip()[:90] for line in buffer.getvalue().splitlines() if "slow_dedupe" in line][:1])

# --- Amostragem: um perfil estatístico, sem instrumentar cada chamada ------------------------------------------------------
elapsed, output = seconds([sys.executable, "-m", "profiling.sampling", "run", str(HERE / "workload.py")])
rows = [line.split() for line in output.splitlines() if re.search(r"workload.py:\d+\(", line)]
print("amostragem, 3 primeiras linhas (nsamples, %, função):")
for row in rows[:3]:
    print("  ", row[0], row[1], row[-1])

# --- O custo de cada profiler -------------------------------------------------------------------------------------------------
print("tempo total de cada execução (s):")
for label, command, target in [
    ("sem profiler", [sys.executable], "workload.py"),
    ("cProfile (tracing)", [sys.executable, "-m", "profiling.tracing", "-o", "NUL" if sys.platform == "win32" else "/dev/null"], "workload.py"),
    ("amostragem", [sys.executable, "-m", "profiling.sampling", "run"], "workload.py"),
]:
    t, _ = seconds([*command, str(HERE / target)])
    print(f"  workload (poucas chamadas)   {label:<20}{t:6.2f}")
for label, command, target in [
    ("sem profiler", [sys.executable], "many_calls.py"),
    ("cProfile (tracing)", [sys.executable, "-m", "profiling.tracing", "-o", "NUL" if sys.platform == "win32" else "/dev/null"], "many_calls.py"),
    ("amostragem", [sys.executable, "-m", "profiling.sampling", "run"], "many_calls.py"),
]:
    t, _ = seconds([*command, str(HERE / target)])
    print(f"  many_calls (7 milhões de chamadas) {label:<20}{t:6.2f}")
