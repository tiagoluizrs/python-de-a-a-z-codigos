"""Gabarito do exercício 3."""
from collections import Counter


def parse_lines(lines):
    for n, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        parts = line.strip().split(None, 4)
        if len(parts) < 5 or not parts[3].endswith(":"):
            raise ValueError(f"linha {n} inválida: {line!r}")
        yield {"time": f"{parts[0]} {parts[1]}", "level": parts[2], "source": parts[3][:-1], "message": parts[4]}


def only_levels(records, *levels):
    for record in records:
        if record["level"] in levels:
            yield record


def only_source(records, prefix):
    for record in records:
        if record["source"].startswith(prefix):
            yield record


def take(records, n):
    if n < 0:
        raise ValueError("n negativo")

    def generator():
        if n == 0:
            return
        for i, record in enumerate(records, start=1):
            yield record
            if i >= n:
                return

    return generator()


def count_by(records, field):
    counts = Counter(record[field] for record in records)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def errors_per_source(lines, limit=None):
    records = only_levels(parse_lines(lines), "ERROR", "CRITICAL")
    if limit is not None:
        records = take(records, limit)
    return count_by(records, "source")

