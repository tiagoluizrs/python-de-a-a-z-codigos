"""Gabarito do exercício 1."""
import csv
import io
import json


def parse_csv(text):
    return [dict(row) for row in csv.DictReader(io.StringIO(text))]


def parse_json(text):
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("json deve ser uma lista")
    return data


def parse_lines(text):
    return [{"line": line.strip()} for line in text.splitlines() if line.strip()]


PARSERS = {"csv": parse_csv, "json": parse_json, "lines": parse_lines}


def make_parser(fmt):
    key = fmt.strip().lower()
    try:
        return PARSERS[key]
    except KeyError:
        raise ValueError(f"formato desconhecido: {fmt!r}; disponíveis: {', '.join(sorted(PARSERS))}") from None


def parse(text, fmt):
    return make_parser(fmt)(text)


def register_parser(fmt):
    key = fmt.lower()

    def decorator(fn):
        if key in PARSERS:
            raise ValueError(f"formato já registrado: {key}")
        PARSERS[key] = fn
        return fn

    return decorator
