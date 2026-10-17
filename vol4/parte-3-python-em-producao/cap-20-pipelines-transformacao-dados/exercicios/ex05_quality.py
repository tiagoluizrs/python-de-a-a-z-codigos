"""Exercício 5: expectativas de qualidade sobre linhas (dicts), um relatório e um portão que interrompe o pipeline."""
from dataclasses import dataclass


class DataQualityError(Exception):
    pass


@dataclass(frozen=True)
class Check:
    name: str
    predicate: object                  # callable(row) -> True quando a linha é BOA
    severity: str = "error"            # "error" ou "warn"
    tolerance: float = 0.0             # fração de linhas ruins que ainda é aceitável


def not_null(column: str) -> Check:
    """Linha boa: ``row.get(column)`` não é ``None`` nem texto vazio/só espaços. ``name``: ``"<column> não nulo"``."""
    raise NotImplementedError


def in_range(column: str, low: float, high: float) -> Check:
    """Linha boa: o valor é número (``int``/``float``, não ``bool``) entre ``low`` e ``high`` INCLUSIVE; ausente ou não numérico é
    ruim. ``name``: ``"<column> em [<low>, <high>]"`` (ex.: ``"qty em [1, 100]"``)."""
    raise NotImplementedError


def one_of(column: str, allowed: set) -> Check:
    """Linha boa: o valor está em ``allowed``. ``name``: ``"<column> permitido"``."""
    raise NotImplementedError


def unique_rows(rows: list[dict], column: str) -> list[dict]:
    """As linhas cujo valor de ``column`` aparece MAIS DE UMA VEZ em ``rows`` (todas as cópias, na ordem original)."""
    raise NotImplementedError


def run_checks(rows: list[dict], checks: list[Check], unique: tuple[str, ...] = ()) -> dict:
    """Roda cada ``Check`` (e a unicidade de cada coluna de ``unique``, com ``name = "<coluna> único"`` e ``severity="error"``,
    tolerância 0) sobre ``rows`` e devolve ``{"total": n, "checks": [{"name", "bad", "ratio", "tolerance", "status"}, ...]}`` na ordem
    dos checks (as unicidades depois). ``ratio`` é ``bad / total`` arredondado a 4 casas (``0.0`` se ``total == 0``); ``status`` é
    ``"ok"`` se ``ratio <= tolerance``; senão ``"fail"`` (severity error) ou ``"warn"`` (severity warn). Uma exceção dentro de um
    ``predicate`` conta a linha como RUIM."""
    raise NotImplementedError


def gate(report: dict) -> None:
    """Levanta ``DataQualityError`` se algum check tem ``status == "fail"``; a mensagem lista TODOS os que falharam, separados por
    ``"; "``, como ``"<name>: <ratio:.2%> > <tolerance:.2%>"``. Só avisos ou tudo ok: não levanta."""
    raise NotImplementedError


def split(rows: list[dict], checks: list[Check]) -> tuple[list[dict], list[dict]]:
    """``(boas, ruins)``, mantendo a ordem: uma linha é boa se passa em TODOS os checks de severidade ``"error"`` (os ``"warn"``
    não separam nada)."""
    raise NotImplementedError
