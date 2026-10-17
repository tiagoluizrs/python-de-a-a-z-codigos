"""Exercício 3: uma classe abstrata com método-gabarito."""
from abc import ABC


class Exporter(ABC):
    """Contrato para exportadores.

    * propriedade abstrata ``extension`` (texto, sem ponto);
    * método abstrato ``render(rows)``: converte uma lista de dicts em texto;
    * método CONCRETO ``save(directory, stem, rows)``: monta
      ``<directory>/<stem>.<extension>``, grava o texto de ``render`` em UTF-8
      e devolve o ``Path`` do arquivo (esse é o Template Method).
    """


class CsvExporter(Exporter):
    """``extension == "csv"``; ``render`` usa cabeçalho com as chaves do
    primeiro dict e uma linha por registro, separadas por vírgula, com quebra
    de linha ``\\n`` entre linhas e SEM linha final em branco."""


class JsonExporter(Exporter):
    """``extension == "json"``; ``render`` devolve ``json.dumps(rows,
    ensure_ascii=False, indent=2)``."""
