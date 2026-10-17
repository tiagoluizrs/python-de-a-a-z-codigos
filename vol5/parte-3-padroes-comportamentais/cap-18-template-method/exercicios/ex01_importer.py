"""Exercício 1: o Template Method clássico: o roteiro de uma importação na classe base, os passos nas subclasses."""
import csv
import io
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import final


@dataclass
class Result:
    rows: list = field(default_factory=list)       # as linhas aceitas (já transformadas)
    errors: list = field(default_factory=list)     # tuplas (índice, mensagem)

    @property
    def ok(self) -> int:
        return len(self.rows)


class Importer(ABC):
    """O ESQUELETO, ``run(raw) -> Result`` (marcado com ``@final``: subclasses não o sobrescrevem). A ORDEM é:

    1. ``self.before()`` (gancho; não faz nada por padrão);
    2. ``self.parse(raw)`` (passo ABSTRATO: devolve um iterável de dicts); ``parse`` que levanta exceção: ``after`` AINDA é chamado (com o resultado vazio) e a exceção sobe;
    3. para cada linha, na ordem (índice a partir de 0): ``self.validate(linha)`` (padrão: aceita tudo; pode levantar ``ValueError``, que registra ``(índice, str(erro))``
       em ``errors`` e PULA a linha); se passar, ``self.transform(linha)`` (padrão: devolve a linha como está) e o resultado entra em ``rows``;
    4. ``self.save(rows)`` (passo ABSTRATO, chamado UMA vez com as linhas aceitas, mesmo se forem zero; se levantar exceção, ``after`` ainda é chamado e a exceção sobe);
    5. ``self.after(result)`` (gancho; recebe o ``Result``; chamado SEMPRE, inclusive nos erros de ``parse`` e ``save``, depois de tudo).
    Devolve o ``Result``."""

    @final
    def run(self, raw) -> Result:
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw):
        ...

    @abstractmethod
    def save(self, rows: list) -> None:
        ...

    def validate(self, row: dict) -> None:
        raise NotImplementedError

    def transform(self, row: dict) -> dict:
        raise NotImplementedError

    def before(self) -> None:
        raise NotImplementedError

    def after(self, result: Result) -> None:
        raise NotImplementedError


class CsvImporter(Importer):
    """``CsvImporter(sink)``: ``sink`` é uma lista onde ``save`` faz ``extend`` das linhas. ``parse``: ``csv.DictReader`` sobre o texto, devolvendo uma lista de ``dict``."""

    def __init__(self, sink: list):
        raise NotImplementedError

    def parse(self, raw):
        raise NotImplementedError

    def save(self, rows):
        raise NotImplementedError


class JsonImporter(Importer):
    """``JsonImporter(sink)``: ``parse`` faz ``json.loads`` e EXIGE uma lista de objetos (senão ``ValueError("json deve ser uma lista")``); ``save`` faz ``extend`` em ``sink``."""

    def __init__(self, sink: list):
        raise NotImplementedError

    def parse(self, raw):
        raise NotImplementedError

    def save(self, rows):
        raise NotImplementedError
