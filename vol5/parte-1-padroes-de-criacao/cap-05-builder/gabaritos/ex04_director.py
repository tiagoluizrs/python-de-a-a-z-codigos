"""Gabarito do exercício 4."""
import csv
import io


class TextBuilder:
    def __init__(self):
        self._lines = []

    def title(self, text):
        self._lines.append(text.upper())

    def row(self, name, value):
        self._lines.append(f"- {name}: {value}")

    def result(self):
        return "\n".join(self._lines)


class MarkdownBuilder:
    def __init__(self):
        self._title = ""
        self._rows = []

    def title(self, text):
        self._title = f"# {text}"

    def row(self, name, value):
        self._rows.append(f"- **{name}**: {value}")

    def result(self):
        return "\n".join([self._title] + ([""] + self._rows if self._rows else []))


class CsvBuilder:
    def __init__(self):
        self._buffer = io.StringIO()
        self._writer = csv.writer(self._buffer, lineterminator="\n")
        self._writer.writerow(["nome", "valor"])

    def title(self, text):
        pass

    def row(self, name, value):
        self._writer.writerow([name, value])

    def result(self):
        return self._buffer.getvalue()


def build_report(builder, title, rows):
    if not title:
        raise ValueError("título obrigatório")
    builder.title(title)
    for name, value in rows:
        builder.row(name, value)
    return builder.result()


def build_all(builders, title, rows):
    return {name: build_report(builder, title, rows) for name, builder in builders.items()}
