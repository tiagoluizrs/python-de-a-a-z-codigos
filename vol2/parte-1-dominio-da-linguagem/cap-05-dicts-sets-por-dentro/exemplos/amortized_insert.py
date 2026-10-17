"""Inserção em dict: custo amortizado constante, com picos no resize."""
import time

for n in (10_000, 100_000, 1_000_000):
    table = {}
    start = time.perf_counter()
    for i in range(n):
        table[i] = i
    per_insert = (time.perf_counter() - start) / n
    print(f"{n:>9,} inserções: {per_insert * 1e9:6.0f} ns por inserção")

table, times = {}, []
for i in range(200_000):
    start = time.perf_counter_ns()
    table[i] = i
    times.append(time.perf_counter_ns() - start)
ordered = sorted(times)
median = ordered[len(ordered) // 2]
print(f"mediana {median} ns | p99,9 {ordered[int(len(ordered) * .999)]} ns"
      f" | máximo {ordered[-1]:,} ns")
spikes = [i for i, t in enumerate(times) if t > 20 * median and t > 10_000]
print("inserções lentas nos tamanhos:", spikes[:10])
