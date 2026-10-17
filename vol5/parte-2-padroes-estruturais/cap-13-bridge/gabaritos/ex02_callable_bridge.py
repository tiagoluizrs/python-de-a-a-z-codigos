"""Gabarito do exercício 2."""
import csv
import io
import json


def _check(rows):
    if not rows:
        raise ValueError("sem linhas")


class CsvExporter:
    def __init__(self, write, delimiter=","):
        self._write, self._delimiter = write, delimiter

    def _line(self, values):
        buffer = io.StringIO()
        csv.writer(buffer, delimiter=self._delimiter, lineterminator="").writerow(values)
        return buffer.getvalue()

    def export(self, rows):
        _check(rows)
        columns = list(rows[0])
        self._write(self._line(columns))
        for row in rows:
            self._write(self._line([row[c] for c in columns]))


class JsonLinesExporter:
    def __init__(self, write):
        self._write = write

    def export(self, rows):
        _check(rows)
        for row in rows:
            self._write(json.dumps(row, ensure_ascii=False, sort_keys=True))


class TableExporter:
    def __init__(self, write):
        self._write = write

    def export(self, rows):
        _check(rows)
        columns = list(rows[0])
        widths = [max(len(str(c)), *(len(str(r[c])) for r in rows)) for c in columns]

        def line(values):
            return " | ".join(str(v).ljust(w) for v, w in zip(values, widths)).rstrip()

        self._write(line(columns))
        self._write("-+-".join("-" * w for w in widths))
        for row in rows:
            self._write(line([row[c] for c in columns]))


def list_writer(target):
    return target.append


def prefixed(write, prefix):
    return lambda line: write(prefix + line)


def fan_out(*writers):
    if not writers:
        raise ValueError("nenhum destino")

    def write(line):
        first = None
        for w in writers:
            try:
                w(line)
            except BaseException as error:
                first = first or error
        if first:
            raise first

    return write


class FileWriter:
    def __init__(self, path):
        self._file = open(path, "w", encoding="utf-8", newline="\n")

    def __call__(self, line):
        if self._file.closed:
            raise ValueError("destino fechado")
        self._file.write(line + "\n")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self._file.close()
