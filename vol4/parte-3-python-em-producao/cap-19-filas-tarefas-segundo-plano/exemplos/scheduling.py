"""Tarefas agendadas: deriva, execuções perdidas, sobreposição e o horário de verão."""
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# 1. a deriva: "dormir 1 segundo" repetido NÃO é "a cada segundo"
def relative_loop(period: float, ticks: int) -> list[float]:
    start, stamps = time.perf_counter(), []
    for _ in range(ticks):
        time.sleep(period)
        time.sleep(0.004)                       # 4 ms de trabalho a cada volta
        stamps.append(time.perf_counter() - start)
    return stamps


def absolute_loop(period: float, ticks: int) -> list[float]:
    start = time.perf_counter()
    stamps = []
    for n in range(1, ticks + 1):
        time.sleep(max(start + n * period - time.perf_counter(), 0))      # alvo ABSOLUTO: o erro não se acumula
        time.sleep(0.004)
        stamps.append(time.perf_counter() - start)
    return stamps


rel, ab = relative_loop(0.05, 40), absolute_loop(0.05, 40)
print(f"40 execuções 'a cada 50 ms' (esperado terminar em 2.000 ms): relativo {rel[-1] * 1e3:6.0f} ms (deriva {(rel[-1] - 2.0) * 1e3:+5.0f} ms) | absoluto {ab[-1] * 1e3:6.0f} ms (deriva {(ab[-1] - 2.0) * 1e3:+5.0f} ms)")


# 2. sobreposição: a execução das 10:00 ainda roda quando chega a das 10:01
running = threading.Lock()
log: list[str] = []


def job(n: int, guarded: bool) -> None:
    if guarded and not running.acquire(blocking=False):
        log.append(f"#{n} pulada: a anterior ainda roda")
        return
    try:
        log.append(f"#{n} começou")
        time.sleep(0.15)                      # demora mais que o intervalo (0,05 s)
        log.append(f"#{n} terminou")
    finally:
        if guarded and running.locked():
            running.release()


for guarded in (False, True):
    log.clear()
    threads = []
    for n in range(4):
        t = threading.Thread(target=job, args=(n, guarded))
        t.start()
        threads.append(t)
        time.sleep(0.05)
    for t in threads:
        t.join()
    simultaneous = max(sum(1 for entry in log[:i + 1] if "começou" in entry) - sum(1 for entry in log[:i + 1] if "terminou" in entry) for i in range(len(log)))
    print(f"\n{'COM trava' if guarded else 'SEM trava'}: no máximo {simultaneous} execuções ao mesmo tempo | {[e for e in log if 'pulada' in e] or 'nenhuma pulada'}")


# 3. horário de verão: "todo dia às 02:30 em Nova York" -- nem todo dia 02:30 existe, e um dia o 01:30 se repete
NY = ZoneInfo("America/New_York")


def next_daily(after: datetime, hour: int, minute: int, tz: ZoneInfo) -> datetime:
    candidate = after.astimezone(tz).replace(hour=hour, minute=minute, second=0, microsecond=0)
    return candidate if candidate > after else candidate + timedelta(days=1)


print("\nhorário de verão em Nova York:")
before = datetime(2026, 3, 7, 12, 0, tzinfo=NY)
wanted = next_daily(before, 2, 30, NY)                                     # "2026-03-08 02:30" no relógio de Nova York
instant = wanted.astimezone(timezone.utc)
print(f"  pedimos 02:30 locais de 8/3: o Python guarda {wanted.isoformat()} (esse horário NÃO existe: o relógio vai de 01:59 a 03:00)")
print(f"  o instante real a que isso corresponde: {instant.strftime('%H:%M UTC')} = {instant.astimezone(NY).strftime('%H:%M %Z')} local -> a tarefa rodaria às 03:30, uma hora depois do esperado")
a = datetime(2026, 11, 1, 1, 30, tzinfo=NY, fold=0)
b = datetime(2026, 11, 1, 1, 30, tzinfo=NY, fold=1)
print(f"  2026-11-01 01:30 local ocorre DUAS vezes: {a.astimezone(timezone.utc).strftime('%H:%M UTC')} (EDT) e {b.astimezone(timezone.utc).strftime('%H:%M UTC')} (EST) -> uma tarefa 'às 01:30' roda duas vezes ou nenhuma")
print("  regra: agende em UTC (ou em um fuso sem horário de verão), e converta só para exibir; tarefas 'às 02:30 locais' precisam de política explícita")

# 4. execuções perdidas: o agendador ficou fora do ar; ao voltar, rodar tudo, só a última ou nenhuma?
scheduled = [datetime(2026, 10, 13, 10, 0, tzinfo=timezone.utc) + timedelta(minutes=5 * k) for k in range(12)]
down_from, down_to = scheduled[3] - timedelta(minutes=1), scheduled[9] + timedelta(minutes=1)
missed = [s for s in scheduled if down_from < s < down_to]
print(f"\nagendador fora do ar por {(down_to - down_from).total_seconds() / 60:.0f} min: {len(missed)} execuções perdidas; políticas: recuperar todas ({len(missed)}), só a mais recente (1), nenhuma (0)")
print("  um relatório diário: recuperar a última | uma limpeza: pular | um fechamento mensal: recuperar TODAS, na ordem")
