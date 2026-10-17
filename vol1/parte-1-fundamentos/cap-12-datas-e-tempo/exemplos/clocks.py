"""time.time x monotonic x perf_counter, e relógio que volta."""
import time

for name in ("time", "monotonic", "perf_counter"):
    info = time.get_clock_info(name)
    print(f"{name:13} {info.implementation:30} "
          f"monotonic={info.monotonic} adjustable={info.adjustable} "
          f"res={info.resolution}")

# Custo de ler cada relógio (medido).
for func in (time.time, time.monotonic, time.perf_counter):
    start = time.perf_counter_ns()
    for _ in range(100_000):
        func()
    per_call = (time.perf_counter_ns() - start) / 100_000
    print(f"{func.__name__:13} {per_call:6.0f} ns por chamada")

# time.sleep nunca dorme "exatamente" o pedido.
for wanted in (0.0001, 0.001, 0.01):
    start = time.perf_counter()
    time.sleep(wanted)
    actual = time.perf_counter() - start
    print(f"sleep({wanted}) levou {actual * 1000:.3f} ms")

# Simulação: o relógio de parede é ajustado para trás (NTP, horário
# de verão do SO, alguém mexeu na hora). time.time() mente.
def fake_wall_clock():
    yield 1_000.0    # início
    yield 940.0      # 60 s atrás!

ticks = fake_wall_clock()
begin, end = next(ticks), next(ticks)
print("duração pelo relógio de parede:", end - begin, "s")

begin_m = time.monotonic()
time.sleep(0.01)
print("duração monotônica >= 0:", time.monotonic() - begin_m >= 0)

# Medir um trecho: perf_counter_ns evita erro de float em medições curtas.
start = time.perf_counter_ns()
total = sum(range(1_000_000))
elapsed = time.perf_counter_ns() - start
print(f"sum(range(10**6)) = {total} em {elapsed / 1e6:.2f} ms")
