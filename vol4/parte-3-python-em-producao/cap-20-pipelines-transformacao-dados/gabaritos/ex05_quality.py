"""Gabarito do exercício 5."""
from collections import Counter
from dataclasses import dataclass


class DataQualityError(Exception):
    pass


@dataclass(frozen=True)
class Check:
    name: str
    predicate: object
    severity: str = "error"
    tolerance: float = 0.0


def not_null(column):
    def good(row):
        value = row.get(column)
        return value is not None and not (isinstance(value, str) and not value.strip())
    return Check(f"{column} não nulo", good)


def in_range(column, low, high):
    def good(row):
        value = row.get(column)
        return isinstance(value, (int, float)) and not isinstance(value, bool) and low <= value <= high
    return Check(f"{column} em [{low}, {high}]", good)


def one_of(column, allowed):
    return Check(f"{column} permitido", lambda row: row.get(column) in allowed)


def unique_rows(rows, column):
    counts = Counter(r.get(column) for r in rows)
    return [r for r in rows if counts[r.get(column)] > 1]


def _safe(predicate, row):
    try:
        return bool(predicate(row))
    except Exception:
        return False


def run_checks(rows, checks, unique=()):
    total = len(rows)
    results = []
    for check in checks:
        bad = sum(1 for r in rows if not _safe(check.predicate, r))
        results.append((check.name, bad, check.tolerance, check.severity))
    for column in unique:
        results.append((f"{column} único", len(unique_rows(rows, column)), 0.0, "error"))
    out = []
    for name, bad, tolerance, severity in results:
        ratio = round(bad / total, 4) if total else 0.0
        status = "ok" if ratio <= tolerance else ("fail" if severity == "error" else "warn")
        out.append({"name": name, "bad": bad, "ratio": ratio, "tolerance": tolerance, "status": status})
    return {"total": total, "checks": out}


def gate(report):
    failed = [c for c in report["checks"] if c["status"] == "fail"]
    if failed:
        raise DataQualityError("; ".join(f"{c['name']}: {c['ratio']:.2%} > {c['tolerance']:.2%}" for c in failed))


def split(rows, checks):
    blocking = [c for c in checks if c.severity == "error"]
    good, bad = [], []
    for row in rows:
        (good if all(_safe(c.predicate, row) for c in blocking) else bad).append(row)
    return good, bad
