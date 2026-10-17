"""Lei de Amdahl: o ganho total de acelerar uma parte é limitado pelo tamanho dela."""
import time

import workload


def timed(func, *args):
    start = time.perf_counter()
    func(*args)
    return time.perf_counter() - start


data = [i % 2000 for i in range(30_000)]
slow = timed(workload.slow_dedupe, data)
fast = timed(workload.fast_dedupe, data)
other = timed(workload.checksum, workload.make_strings(20_000)) + timed(workload.make_strings, 20_000)
total_before = slow + other
total_after = fast + other
fraction = slow / total_before
print(f"parte lenta = {fraction * 100:.1f}% do total | speedup da parte: {slow / fast:.0f}x | speedup do programa: {total_before / total_after:.1f}x")


def amdahl(fraction, factor):
    return 1 / ((1 - fraction) + fraction / factor)


print("previsão de Amdahl para a parte lenta", f"{amdahl(fraction, slow / fast):.1f}x")
for fraction_demo in (0.5, 0.9, 0.99):
    print(f"  se uma parte de {fraction_demo * 100:.0f}% ficar INFINITAMENTE rápida, o programa fica no máximo {amdahl(fraction_demo, 1e12):.0f}x mais rápido")
