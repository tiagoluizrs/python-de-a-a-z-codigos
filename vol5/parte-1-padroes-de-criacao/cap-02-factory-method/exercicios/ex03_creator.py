"""Exercício 3: o Factory Method CLÁSSICO (criador abstrato + subclasses) e a sua versão em função, lado a lado."""
import csv
import io
import json
from abc import ABC, abstractmethod


class CsvWriter:
    """``write_header(columns)``, ``write_row(values)`` e ``result() -> str``. Saída CSV com ``"\\n"`` como fim de linha (``csv.writer`` com
    ``lineterminator="\\n"`` sobre um ``io.StringIO``)."""

    def write_header(self, columns: list[str]) -> None:
        raise NotImplementedError

    def write_row(self, values: list) -> None:
        raise NotImplementedError

    def result(self) -> str:
        raise NotImplementedError


class JsonWriter:
    """Mesma interface; acumula os registros (cada linha vira um dict com as colunas do cabeçalho) e ``result()`` devolve
    ``json.dumps(registros, ensure_ascii=False)``."""

    def write_header(self, columns: list[str]) -> None:
        raise NotImplementedError

    def write_row(self, values: list) -> None:
        raise NotImplementedError

    def result(self) -> str:
        raise NotImplementedError


class Exporter(ABC):
    """O CRIADOR: ``export(rows)`` cria um escritor com ``self.create_writer()`` (UMA vez por exportação), escreve o cabeçalho (as chaves da
    primeira linha, na ordem), depois os valores de cada linha NA ORDEM DO CABEÇALHO, e devolve ``writer.result()``.
    ``rows`` vazio: ``ValueError("sem linhas")``. Uma linha sem alguma coluna do cabeçalho: ``KeyError(coluna)``."""

    @abstractmethod
    def create_writer(self):
        ...

    def export(self, rows: list[dict]) -> str:
        raise NotImplementedError


class CsvExporter(Exporter):
    def create_writer(self):
        raise NotImplementedError


class JsonExporter(Exporter):
    def create_writer(self):
        raise NotImplementedError


def export_with(create_writer, rows: list[dict]) -> str:
    """A MESMA lógica de ``Exporter.export``, mas recebendo a fábrica (um callable sem argumentos) em vez de herdar. Escreva-a primeiro e faça
    ``Exporter.export`` chamá-la: ``return export_with(self.create_writer, rows)``."""
    raise NotImplementedError
