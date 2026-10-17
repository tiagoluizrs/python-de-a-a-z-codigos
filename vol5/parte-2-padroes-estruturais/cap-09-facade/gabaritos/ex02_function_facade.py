"""Gabarito do exercício 2."""
import csv
import json
from pathlib import Path


class ConversionError(Exception):
    pass


def _convert(value):
    for kind in (int, float):
        try:
            return kind(value)
        except ValueError:
            continue
    return value


def csv_to_json(src, dst, *, delimiter=",", numeric=True, encoding="utf-8"):
    src, dst = Path(src), Path(dst)
    try:
        text = src.read_text(encoding=encoding, newline="")
    except FileNotFoundError:
        raise ConversionError(f"arquivo não encontrado: {src}") from None
    reader = csv.reader(text.splitlines(), delimiter=delimiter)
    try:
        header = next(reader)
    except StopIteration:
        raise ConversionError("csv vazio") from None
    records = []
    for n, row in enumerate(reader, start=2):
        if len(row) > len(header):
            raise ConversionError(f"linha {n} tem colunas demais")
        row = row + [""] * (len(header) - len(row))
        records.append({h: (_convert(v) if numeric and v.strip() else v) for h, v in zip(header, row)})
    tmp = dst.with_name(dst.name + ".tmp")
    try:
        tmp.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(dst)
    finally:
        if tmp.exists():
            tmp.unlink()
    return len(records)
