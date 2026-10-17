"""Exercício 5: buscar resultados grandes em lotes (arraysize)."""


def choose_arraysize(row_bytes, target_batch_bytes=1_000_000, minimum=10, maximum=10_000):
    """Quantas linhas buscar por ida e volta: ``target_batch_bytes // row_bytes``, limitado a
    ``[minimum, maximum]``. ``row_bytes <= 0`` ou ``minimum > maximum`` levantam ``ValueError``."""
    raise NotImplementedError


def fetch_in_batches(cursor, size):
    """Gerador que devolve LISTAS de até ``size`` linhas (``cursor.fetchmany(size)``) até
    esgotar o cursor, sem nunca carregar tudo; ``size < 1`` levanta ``ValueError``. O cursor
    pode ser de qualquer driver DB-API."""
    raise NotImplementedError
    yield  # pragma: no cover
