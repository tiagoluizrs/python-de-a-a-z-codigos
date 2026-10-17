"""Gabarito do exercício 1."""
import csv
import io
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import final


@dataclass
class Result:
    rows: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    @property
    def ok(self):
        return len(self.rows)


class Importer(ABC):
    @final
    def run(self, raw):
        result = Result()
        self.before()
        try:
            for i, row in enumerate(self.parse(raw)):
                try:
                    self.validate(row)
                except ValueError as error:
                    result.errors.append((i, str(error)))
                    continue
                result.rows.append(self.transform(row))
            self.save(result.rows)
        finally:
            self.after(result)
        return result

    @abstractmethod
    def parse(self, raw):
        ...

    @abstractmethod
    def save(self, rows):
        ...

    def validate(self, row):
        pass

    def transform(self, row):
        return row

    def before(self):
        pass

    def after(self, result):
        pass


class CsvImporter(Importer):
    def __init__(self, sink):
        self.sink = sink

    def parse(self, raw):
        return list(csv.DictReader(io.StringIO(raw)))

    def save(self, rows):
        self.sink.extend(rows)


class JsonImporter(Importer):
    def __init__(self, sink):
        self.sink = sink

    def parse(self, raw):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("json deve ser uma lista")
        return data

    def save(self, rows):
        self.sink.extend(rows)
