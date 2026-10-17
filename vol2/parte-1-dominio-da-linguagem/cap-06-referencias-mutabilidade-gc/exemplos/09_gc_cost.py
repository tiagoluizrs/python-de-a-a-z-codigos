"""Custo do coletor cíclico em um programa com muitos objetos."""
import gc
import time


class Item:
    def __init__(self, i: int) -> None:
        self.i = i
        self.tags = [i]


def build(n: int) -> list[Item]:
    return [Item(i) for i in range(n)]


def timed(label: str, fn) -> None:
    gc.collect()
    before = [s["collections"] for s in gc.get_stats()]
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    after = [s["collections"] for s in gc.get_stats()]
    runs = [b - a for a, b in zip(before, after)]
    print(f"{label:<30} {elapsed * 1000:7.1f} ms  coletas={runs}")
    return result


N = 1_000_000
print(f"construir {N:,} objetos Item (cada um com uma lista)")
timed("gc ligado", lambda: build(N))
gc.disable()
timed("gc desligado", lambda: build(N))
gc.enable()

print("\ncustos de uma coleta completa")
heap = build(N)
timed("gc.collect() com heap vivo", gc.collect)
gc.freeze()
print("objetos congelados:", f"{gc.get_freeze_count():,}")
timed("gc.collect() após freeze", gc.collect)
extra = timed("+500 mil, heap congelado", lambda: build(N // 2))
del extra
gc.unfreeze()
extra = timed("+500 mil, heap sem freeze", lambda: build(N // 2))
del extra, heap
