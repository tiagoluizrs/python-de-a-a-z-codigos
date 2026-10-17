"""Exercício 5: parser de ISO 8601 estrito, com erros úteis."""
import datetime as dt


def parse_strict(text: str) -> dt.datetime:
    """Aceita SOMENTE ``YYYY-MM-DDTHH:MM:SS[.ffffff]`` seguido de
    ``Z`` ou de um deslocamento ``+HH:MM`` / ``-HH:MM``.

    Exige: separador ``T`` maiúsculo, segundos e fuso explícito.
    Devolve um datetime aware. Para qualquer outra entrada, levante
    ``ValueError`` cuja mensagem contenha ``repr(text)`` e diga QUAL
    regra foi violada (por exemplo: fuso ausente, formato básico sem
    hífens, data impossível, espaço no lugar do ``T``).

    >>> parse_strict("2026-10-12T09:30:00Z").isoformat()
    '2026-10-12T09:30:00+00:00'
    >>> parse_strict("2026-10-12T09:30:00-03:00").utcoffset()
    datetime.timedelta(days=-1, seconds=75600)

    Rejeita (ValueError): "2026-10-12", "2026-10-12T09:30:00",
    "2026-10-12 09:30:00Z", "20261012T093000Z", "2026-02-30T00:00:00Z".

    Dica: valide a FORMA primeiro (``re.fullmatch``) e delegue o
    conteúdo (datas impossíveis) a ``datetime.fromisoformat``.
    """
    raise NotImplementedError
