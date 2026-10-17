"""Exercício 5: calcular execuções agendadas SEM deriva e sem cair nas armadilhas do horário de verão."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def next_every(after: datetime, start: datetime, period: timedelta) -> datetime:
    """A próxima execução de uma tarefa "a cada ``period``" ancorada em ``start`` (todos com fuso; compare em UTC): o primeiro
    instante ``start + k * period`` (``k >= 0``) ESTRITAMENTE depois de ``after``. Sem deriva: o cálculo é sempre a partir de
    ``start``, nunca de "agora + period". ``period`` não positivo: ``ValueError``."""
    raise NotImplementedError


def next_daily(after: datetime, hour: int, minute: int, tz: ZoneInfo) -> datetime:
    """A próxima execução "todo dia às ``hour:minute`` no relógio de ``tz``", estritamente depois de ``after``; devolve um
    ``datetime`` em UTC (``tzinfo`` UTC). Duas armadilhas:

    * horário que NÃO EXISTE (o relógio pula; ex.: 02:30 em 8/3/2026 em Nova York): rode no primeiro instante válido depois do
      salto (03:00 locais, que é 07:00 UTC);
    * horário que ocorre DUAS vezes (o relógio repete; ex.: 01:30 em 1/11/2026 em Nova York): rode só na PRIMEIRA ocorrência
      (``fold=0``), uma vez por dia."""
    raise NotImplementedError


def missed_runs(last_run: datetime, now: datetime, start: datetime, period: timedelta, policy: str, limit: int = 100) -> list[datetime]:
    """As execuções "a cada ``period`` ancorado em ``start``" que ficaram para trás: as de ``last_run`` (exclusive) até ``now``
    (inclusive), em ordem, e o que fazer com elas conforme ``policy``:

    * ``"all"``: todas, mas no máximo as ``limit`` PRIMEIRAS;
    * ``"latest"``: só a mais recente (lista com 1 item, ou vazia se nenhuma);
    * ``"none"``: lista vazia (pule tudo e espere a próxima);
    * outra ``policy``: ``ValueError``."""
    raise NotImplementedError
