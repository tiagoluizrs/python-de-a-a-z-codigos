"""Gabarito do exercício 4."""
import gc
import tracemalloc
from collections.abc import Callable


def leak_growth(func: Callable[[], None], rounds: int = 200) -> int:
    func()                          # aquecimento
    gc.collect()
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    for _ in range(rounds):
        func()
    gc.collect()                    # tira o lixo cíclico do caminho
    after = tracemalloc.take_snapshot()
    tracemalloc.stop()
    diffs = after.compare_to(before, "filename")
    # Só o que cresceu importa; filtra o ruído negativo
    return sum(d.size_diff for d in diffs if d.size_diff > 0)
