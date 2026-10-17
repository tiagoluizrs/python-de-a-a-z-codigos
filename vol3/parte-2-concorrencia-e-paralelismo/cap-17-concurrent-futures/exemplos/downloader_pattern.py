"""Um padrão completo: lote com limite, progresso, erros isolados e relatório."""
import concurrent.futures as cf
import random
import time
from dataclasses import dataclass


@dataclass
class Outcome:
    index: int
    value: object = None
    error: Exception | None = None

    @property
    def ok(self):
        return self.error is None


def fake_download(index):
    time.sleep(0.05 + (index % 4) * 0.02)
    if index % 7 == 3:
        raise ConnectionError(f"item {index}: conexão recusada")
    return f"conteúdo-{index}"


def fetch_all(func, items, workers=8, on_progress=None):
    outcomes = [None] * len(items)
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(func, item): index for index, item in enumerate(items)}
        done = 0
        for future in cf.as_completed(futures):
            index = futures[future]
            try:
                outcomes[index] = Outcome(index, value=future.result())
            except Exception as error:                       # um item ruim não derruba os outros
                outcomes[index] = Outcome(index, error=error)
            done += 1
            if on_progress:
                on_progress(done, len(items))
    return outcomes


if __name__ == "__main__":
    random.seed(1)
    progress = []
    start = time.perf_counter()
    outcomes = fetch_all(fake_download, list(range(30)), workers=10, on_progress=lambda d, n: progress.append(d))
    elapsed = time.perf_counter() - start
    ok = [o for o in outcomes if o.ok]
    failed = [o for o in outcomes if not o.ok]
    print(f"30 itens em {elapsed:.2f} s (sequencial levaria ~{sum(0.05 + (i % 4) * 0.02 for i in range(30)):.1f} s)")
    print(f"sucessos: {len(ok)} | falhas: {len(failed)} -> {[o.index for o in failed]}")
    print("resultados na ORDEM de entrada:", [o.index for o in outcomes][:8], "...")
    print("progresso contou até", progress[-1])
