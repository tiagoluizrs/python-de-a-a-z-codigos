"""Dados em fluxo: janelas de tempo, marca d'água e eventos atrasados, com memória limitada."""
import random
import time
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

WINDOW = 60                                  # segundos


@dataclass(frozen=True)
class Event:
    ts: int                                  # tempo DO EVENTO (quando aconteceu), em segundos
    key: str
    value: float


def stream(n: int, max_delay: int, seed: int = 5) -> Iterator[Event]:
    """Eventos que acontecem em ordem de tempo, mas CHEGAM fora de ordem (rede, filas, fusos): atraso aleatório até ``max_delay``."""
    rng = random.Random(seed)
    events = [Event(ts=i // 20, key=rng.choice(["a", "b", "c"]), value=1.0) for i in range(n)]    # 20 eventos por segundo
    arrival = sorted(((e.ts + min(rng.expovariate(4 / max_delay), max_delay), k, e) for k, e in enumerate(events)), key=lambda x: (x[0], x[1]))
    for _, _, event in arrival:
        yield event


def batch_truth(events: Iterable[Event]) -> dict[tuple[int, str], float]:
    """A resposta certa: agrupa TUDO por (janela, chave). Precisa ter todos os dados na memória."""
    totals: dict[tuple[int, str], float] = defaultdict(float)
    for e in events:
        totals[(e.ts // WINDOW * WINDOW, e.key)] += e.value
    return dict(totals)


class WindowAggregator:
    """Janelas tumbling (de 60 s, sem sobreposição) com marca d'água: uma janela é FECHADA e emitida quando a marca d'água
    (o maior tempo de evento visto, menos a tolerância de atraso) passa do fim dela. O que chega depois disso é DESCARTADO
    (e contado). Só as janelas ABERTAS ficam na memória."""

    def __init__(self, allowed_lateness: int):
        self.lateness = allowed_lateness
        self.open: dict[int, dict[str, float]] = {}
        self.max_ts = -1
        self.dropped = 0
        self.peak_open = 0

    def watermark(self) -> int:
        return self.max_ts - self.lateness

    def process(self, event: Event) -> Iterator[tuple[int, str, float]]:
        start = event.ts // WINDOW * WINDOW
        if start + WINDOW <= self.watermark():                        # a janela deste evento já foi fechada
            self.dropped += 1
            return
        self.open.setdefault(start, defaultdict(float))[event.key] += event.value
        self.max_ts = max(self.max_ts, event.ts)
        self.peak_open = max(self.peak_open, len(self.open))
        for window in sorted(w for w in self.open if w + WINDOW <= self.watermark()):
            for key, total in sorted(self.open.pop(window).items()):
                yield window, key, total

    def flush(self) -> Iterator[tuple[int, str, float]]:
        for window in sorted(self.open):
            for key, total in sorted(self.open.pop(window).items()):
                yield window, key, total


N = 200_000                                  # ~2,8 horas de eventos
MAX_DELAY = 120

events = list(stream(N, MAX_DELAY))
out_of_order = sum(1 for a, b in zip(events, events[1:]) if b.ts < a.ts)
truth = batch_truth(events)
print(f"{N:,} eventos em {events[-1].ts // 60:,} minutos; {out_of_order:,} chegaram FORA DE ORDEM ({out_of_order / N:.0%}); atraso máximo {MAX_DELAY} s")
print(f"resposta em lote (tudo na memória): {len(truth)} totais de (janela, chave); soma {sum(truth.values()):,.0f}\n")

print(f"{'tolerância de atraso':>22} | {'janelas abertas (pico)':>22} | {'descartados':>11} | {'janelas certas':>14} | {'tempo':>7}")
for lateness in (0, 15, 60, 120):
    agg = WindowAggregator(lateness)
    start = time.perf_counter()
    result: dict[tuple[int, str], float] = {}
    for event in events:
        for window, key, total in agg.process(event):
            result[(window, key)] = total
    for window, key, total in agg.flush():
        result[(window, key)] = total
    elapsed = time.perf_counter() - start
    correct = sum(1 for k, v in truth.items() if result.get(k) == v)
    print(f"{lateness:>20} s | {agg.peak_open:>22} | {agg.dropped:>11,} | {correct / len(truth):>14.1%} | {elapsed * 1e3:5.0f} ms")

print("\nquanto MAIS tolerância: mais exato, e mais janelas abertas na memória (e as respostas saem mais tarde)")
print(f"o lote guardou {len(events):,} eventos; o fluxo com 120 s de tolerância guardou no máximo 4 janelas x 3 chaves")
