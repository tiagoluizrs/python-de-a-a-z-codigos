"""Exercício 1: uma fábrica simples de parsers (um dicionário, sem hierarquia), com mensagem de erro útil."""
import csv
import io
import json


def parse_csv(text: str) -> list[dict]:
    """Lê um CSV com cabeçalho (``csv.DictReader``) e devolve uma lista de dicts (``dict(row)``)."""
    raise NotImplementedError


def parse_json(text: str) -> list[dict]:
    """``json.loads``; o resultado PRECISA ser uma lista, senão ``ValueError("json deve ser uma lista")``."""
    raise NotImplementedError


def parse_lines(text: str) -> list[dict]:
    """Cada linha não vazia (depois de ``strip``) vira ``{"line": texto}``."""
    raise NotImplementedError


PARSERS: dict = {}    # preencha com "csv", "json" e "lines"


def make_parser(fmt: str):
    """Devolve a função de parse do formato (sem diferenciar maiúsculas de minúsculas e ignorando espaços nas pontas). Formato desconhecido:
    ``ValueError(f"formato desconhecido: {fmt!r}; disponíveis: csv, json, lines")`` (a lista em ordem alfabética, vinda de ``PARSERS``)."""
    raise NotImplementedError


def parse(text: str, fmt: str) -> list[dict]:
    """Atalho: ``make_parser(fmt)(text)``."""
    raise NotImplementedError


def register_parser(fmt: str):
    """Decorador que registra um parser novo em ``PARSERS`` sob ``fmt`` (minúsculo) e devolve a própria função. Nome já registrado:
    ``ValueError(f"formato já registrado: {fmt}")``."""
    raise NotImplementedError
