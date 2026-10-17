"""Memória: tracemalloc mostra QUEM alocou, o pico e o crescimento."""
import tracemalloc
from pathlib import Path

# --- Pico de memória de uma função ------------------------------------------------------------------------------------
def build_list(n):
    return [str(i) for i in range(n)]


def build_generator_sum(n):
    return sum(len(str(i)) for i in range(n))


for fn in (build_list, build_generator_sum):
    tracemalloc.start()
    fn(200_000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{fn.__name__:<22} pico {peak / 1e6:6.2f} MB | restou ao final {current / 1e6:6.2f} MB")

# --- Instantâneos e a diferença entre eles: achar o vazamento ----------------------------------------------------
cache = []


def leaky_request(i):
    cache.append("x" * 1000 + str(i))             # esqueceu de limpar: cresce a cada chamada


tracemalloc.start()
before = tracemalloc.take_snapshot()
for i in range(2_000):
    leaky_request(i)
after = tracemalloc.take_snapshot()
tracemalloc.stop()
for stat in after.compare_to(before, "lineno")[:1]:
    frame = stat.traceback[0]
    print(f"maior crescimento: {Path(frame.filename).name}:{frame.lineno} +{stat.size_diff / 1e6:.2f} MB ({stat.count_diff:+d} blocos)")

# --- Os maiores alocadores ------------------------------------------------------------------------------------------
tracemalloc.start()
data = {i: [i] * 10 for i in range(20_000)}
snapshot = tracemalloc.take_snapshot()
tracemalloc.stop()
top = snapshot.statistics("lineno")[0]
print(f"maior alocador: {Path(top.traceback[0].filename).name}:{top.traceback[0].lineno} -> {top.size / 1e6:.2f} MB em {top.count} blocos")

# --- O custo do próprio tracemalloc ---------------------------------------------------------------------------------------
import time

start = time.perf_counter()
build_list(200_000)
plain = time.perf_counter() - start
tracemalloc.start()
start = time.perf_counter()
build_list(200_000)
traced = time.perf_counter() - start
tracemalloc.stop()
print(f"build_list(200_000): sem tracemalloc {plain * 1e3:.1f} ms | com {traced * 1e3:.1f} ms ({traced / plain:.1f}x)")
