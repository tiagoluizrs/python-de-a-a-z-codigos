"""Gabarito do exercício 2."""
import csv
import json
from collections.abc import Callable
from pathlib import Path


def csv_to_json(csv_path: Path, json_path: Path,
                types: dict[str, Callable]) -> int:
    records = []
    # utf-8-sig remove o BOM se existir e não atrapalha se não existir
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            record = {}
            for column, value in row.items():
                if value == "":
                    record[column] = None
                else:
                    convert = types.get(column, str)
                    record[column] = convert(value)
            records.append(record)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    return len(records)
