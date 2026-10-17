"""Medir tempo direito: relógios, repetições, mínimo x média, e as armadilhas."""
import statistics
import time
import timeit

# --- Os relógios -----------------------------------------------------------------------------------------------
for name in ("time", "perf_counter", "monotonic", "process_time"):
    info = time.get_clock_info(name)
    print(f"{name:<13} resolução {info.resolution:.0e} s | monótono: {info.monotonic} | ajustável: {info.adjustable}")

# perf_counter: o certo para medir DURAÇÃO; time.time: o relógio da parede (pode saltar)
start = time.perf_counter()
sum(range(1_000_000))
print(f"sum(range(1_000_000)) levou {(time.perf_counter() - start) * 1e3:.2f} ms em UMA medição")

# --- Uma medição é uma amostra, não a verdade ---------------------------------------------------------------------
samples = [timeit.timeit("sum(range(100_000))", number=100) / 100 * 1e6 for _ in range(15)]
print(f"15 medições de sum(range(100_000)) em us: min {min(samples):.0f} | mediana {statistics.median(samples):.0f} | "
      f"média {statistics.mean(samples):.0f} | máx {max(samples):.0f} | desvio {statistics.stdev(samples):.0f}")
print("regra: repita e use o MÍNIMO (o menor tempo é o menos perturbado pelo ruído do sistema)")

# --- Armadilha 1: o compilador dobra constantes ------------------------------------------------------------------
constant = timeit.timeit("60 * 60 * 24", number=5_000_000)
variable = timeit.timeit("a * b * c", setup="a, b, c = 60, 60, 24", number=5_000_000)
print(f"60 * 60 * 24 (constante dobrada): {constant / 5 * 1e3:.1f} ns | a * b * c (calculado de verdade): {variable / 5 * 1e3:.1f} ns")

# --- Armadilha 2: o setup entrando na conta -------------------------------------------------------------------------
with_setup = timeit.timeit("data = list(range(10_000)); sum(data)", number=2_000)
sum_only = timeit.timeit("sum(data)", setup="data = list(range(10_000))", number=2_000)
print(f"construir a lista + somar: {with_setup / 2_000 * 1e6:.0f} us | só somar (lista no setup): {sum_only / 2_000 * 1e6:.0f} us")

# --- Armadilha 3: ordenar uma lista JÁ ordenada não mede o caso real ----------------------------------------------
import random

random.seed(1)
shuffled = random.sample(range(10_000), 10_000)
t_sorted = min(timeit.repeat("sorted(data)", globals={"data": list(range(10_000))}, number=300, repeat=5)) / 300
t_shuffled = min(timeit.repeat("sorted(data)", globals={"data": shuffled}, number=300, repeat=5)) / 300
print(f"sorted() em lista ordenada: {t_sorted * 1e6:.0f} us | embaralhada: {t_shuffled * 1e6:.0f} us ({t_shuffled / t_sorted:.0f}x)")

# --- Armadilha 4: o coletor de lixo e o timeit -----------------------------------------------------------------------------
print("timeit desliga o coletor de lixo durante a medição por padrão; o programa real não")
