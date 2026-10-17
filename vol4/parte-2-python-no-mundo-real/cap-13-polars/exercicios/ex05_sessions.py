"""Exercício 5: sessões a partir de eventos (diff, cum_sum e over)."""
import polars as pl


def sessionize(events: pl.DataFrame, gap_minutes: int = 30) -> pl.DataFrame:
    """``events`` tem ``user`` (String) e ``ts`` (Datetime), em qualquer ordem. Uma nova sessão de um usuário começa
    quando o intervalo para o evento anterior DO MESMO USUÁRIO é MAIOR que ``gap_minutes`` (igual ao limite continua a
    mesma sessão).

    Devolve os eventos ordenados por ``user`` e ``ts`` com a coluna ``session`` (``1, 2, 3...`` por usuário), em
    uma única passada de expressões (``diff``, ``cum_sum``, ``over``), sem laço Python."""
    raise NotImplementedError


def session_summary(events: pl.DataFrame, gap_minutes: int = 30) -> pl.DataFrame:
    """Uma linha por sessão: ``user``, ``session``, ``start`` (menor ``ts``), ``end`` (maior), ``events`` (``UInt32``)
    e ``minutes`` (duração ``end - start`` em minutos, ``Float64``). Ordenado por ``user`` e ``session``."""
    raise NotImplementedError
