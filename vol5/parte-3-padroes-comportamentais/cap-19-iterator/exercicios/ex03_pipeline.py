"""Exercício 3: um pipeline PREGUIÇOSO de processamento de logs: cada etapa é um gerador que consome um item por vez."""
from collections import Counter


def parse_lines(lines):
    """Para cada linha de texto no formato ``"2026-10-15 12:00:01 ERROR db: disco cheio"`` (data, hora, nível, ``origem:`` e mensagem), produz um dict
    ``{"time": "2026-10-15 12:00:01", "level": "ERROR", "source": "db", "message": "disco cheio"}``. Linhas em branco (só espaços) são IGNORADAS; linhas mal formadas
    (menos de 5 partes, ou a origem sem ``:`` no fim): ``ValueError(f"linha {n} inválida: {linha!r}")`` (``n`` a partir de 1, contando TODAS as linhas lidas, inclusive as em branco),
    levantada quando o item é pedido (preguiça). Preguiçoso: não lê a linha seguinte antes de ela ser necessária."""
    raise NotImplementedError


def only_levels(records, *levels):
    """Mantém só os registros cujo ``level`` está em ``levels`` (sem níveis: nenhum registro). Preguiçoso."""
    raise NotImplementedError


def only_source(records, prefix: str):
    """Mantém só os registros cuja ``source`` começa com ``prefix``. Preguiçoso."""
    raise NotImplementedError


def take(records, n: int):
    """Produz no máximo ``n`` registros e PARA (sem consumir o ``n+1``-ésimo da fonte). ``n < 0``: ``ValueError("n negativo")`` na chamada. ``n == 0``: não consome nada."""
    raise NotImplementedError


def count_by(records, field: str) -> dict:
    """Consome TODOS os registros e devolve ``{valor_do_campo: quantidade}`` como um ``dict`` comum, ordenado da MAIOR para a MENOR quantidade (empates: valor em ordem alfabética)."""
    raise NotImplementedError


def errors_per_source(lines, limit: int | None = None) -> dict:
    """Compõe o pipeline: ``parse_lines`` -> ``only_levels("ERROR", "CRITICAL")`` -> (se ``limit`` não for ``None``, ``take`` dos ``limit`` primeiros) -> ``count_by("source")``.
    Com ``limit``, o pipeline NÃO deve ler mais linhas da fonte do que as necessárias para achar ``limit`` erros."""
    raise NotImplementedError
