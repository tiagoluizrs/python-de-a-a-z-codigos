"""Gabarito do exercício 5."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def next_every(after, start, period):
    if period <= timedelta(0):
        raise ValueError("period deve ser positivo")
    after_utc, start_utc = after.astimezone(UTC), start.astimezone(UTC)
    if after_utc < start_utc:
        return start_utc
    elapsed = after_utc - start_utc
    k = elapsed // period + 1
    return start_utc + k * period


def _to_utc(local_naive: datetime, tz: ZoneInfo) -> datetime | None:
    """Converte um horário de parede para UTC; None se ele não existe; usa a primeira ocorrência se for ambíguo."""
    candidate = local_naive.replace(tzinfo=tz, fold=0)
    roundtrip = candidate.astimezone(UTC).astimezone(tz)
    if roundtrip.replace(tzinfo=None) != local_naive:
        return None
    return candidate.astimezone(UTC)


def next_daily(after, hour, minute, tz):
    after_utc = after.astimezone(UTC)
    day = after.astimezone(tz).date() - timedelta(days=1)
    for _ in range(5):
        wall = datetime(day.year, day.month, day.day, hour, minute)
        instant = _to_utc(wall, tz)
        if instant is None:                                       # o horário não existe: primeiro instante depois do salto
            t = wall.replace(tzinfo=tz, fold=0).astimezone(UTC)
            after_offset = t.astimezone(tz).utcoffset()
            while (t - timedelta(minutes=1)).astimezone(tz).utcoffset() == after_offset:
                t -= timedelta(minutes=1)
            instant = t
        if instant > after_utc:
            return instant
        day += timedelta(days=1)
    raise RuntimeError("sem próxima execução")


def missed_runs(last_run, now, start, period, policy, limit=100):
    if policy not in ("all", "latest", "none"):
        raise ValueError(f"política desconhecida: {policy!r}")
    runs = []
    current = next_every(last_run, start, period)
    now_utc = now.astimezone(UTC)
    while current <= now_utc:
        runs.append(current)
        current = current + period
    if policy == "none":
        return []
    if policy == "latest":
        return runs[-1:]
    return runs[:limit]
