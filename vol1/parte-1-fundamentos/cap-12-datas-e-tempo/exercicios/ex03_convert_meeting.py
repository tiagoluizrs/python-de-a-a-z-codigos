"""Exercício 3: converter um horário de reunião entre fusos."""
import datetime as dt
from zoneinfo import ZoneInfo


def convert_meeting(local: dt.datetime, from_key: str, to_key: str,
                    *, fold: int = 0) -> dt.datetime:
    """Converte um horário de parede (naive) de um fuso para outro.

    - ``local`` é naive, no fuso ``from_key`` (chave IANA).
    - Devolve um datetime aware no fuso ``to_key``.
    - ``fold`` resolve horários ambíguos (0 = primeira ocorrência).
    - Se ``local`` já for aware, levante ``ValueError``.
    - Se o horário NÃO EXISTE em ``from_key`` (salto do horário de
      verão), levante ``ValueError``.

    Exemplo:
    >>> meeting = dt.datetime(2026, 10, 12, 14)
    >>> r = convert_meeting(meeting, "America/Sao_Paulo", "Asia/Tokyo")
    >>> r.isoformat()
    '2026-10-13T02:00:00+09:00'

    Dica: para detectar um horário inexistente, converta para UTC e
    volte; se o horário de parede mudou, ele não existia.
    """
    raise NotImplementedError
