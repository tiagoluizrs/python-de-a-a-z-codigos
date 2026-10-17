"""Gabarito do exercício 3."""
import json
from abc import ABC, abstractmethod
from pathlib import Path


class Exporter(ABC):
    @property
    @abstractmethod
    def extension(self):
        """Extensão sem ponto."""

    @abstractmethod
    def render(self, rows):
        """Converte lista de dicts em texto."""

    def save(self, directory, stem, rows):            # Template Method
        path = Path(directory) / f"{stem}.{self.extension}"
        path.write_text(self.render(rows), encoding="utf-8")
        return path


class CsvExporter(Exporter):
    extension = "csv"

    def render(self, rows):
        if not rows:
            return ""
        header = list(rows[0])
        lines = [",".join(header)]
        lines += [",".join(str(row[key]) for key in header) for row in rows]
        return "\n".join(lines)


class JsonExporter(Exporter):
    extension = "json"

    def render(self, rows):
        return json.dumps(rows, ensure_ascii=False, indent=2)
