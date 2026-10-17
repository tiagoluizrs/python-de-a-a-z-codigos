"""Gabarito do exercício 3."""
import csv
import io
import json
from abc import ABC, abstractmethod


class CsvWriter:
    def __init__(self):
        self._buffer = io.StringIO()
        self._writer = csv.writer(self._buffer, lineterminator="\n")

    def write_header(self, columns):
        self._writer.writerow(columns)

    def write_row(self, values):
        self._writer.writerow(values)

    def result(self):
        return self._buffer.getvalue()


class JsonWriter:
    def __init__(self):
        self._columns: list[str] = []
        self._records: list[dict] = []

    def write_header(self, columns):
        self._columns = list(columns)

    def write_row(self, values):
        self._records.append(dict(zip(self._columns, values)))

    def result(self):
        return json.dumps(self._records, ensure_ascii=False)


def export_with(create_writer, rows):
    if not rows:
        raise ValueError("sem linhas")
    writer = create_writer()
    columns = list(rows[0])
    writer.write_header(columns)
    for row in rows:
        writer.write_row([row[c] for c in columns])
    return writer.result()


class Exporter(ABC):
    @abstractmethod
    def create_writer(self):
        ...

    def export(self, rows):
        return export_with(self.create_writer, rows)


class CsvExporter(Exporter):
    def create_writer(self):
        return CsvWriter()


class JsonExporter(Exporter):
    def create_writer(self):
        return JsonWriter()
