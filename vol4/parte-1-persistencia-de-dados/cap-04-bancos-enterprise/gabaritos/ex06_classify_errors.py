"""Gabarito do exercício 6."""

CATEGORIES = ("duplicate", "deadlock", "timeout", "connection", "other")

_TABLES = {
    "postgresql": {"23505": "duplicate", "40P01": "deadlock", "40001": "deadlock", "57014": "timeout", "55P03": "timeout"},
    "mysql": {1062: "duplicate", 1213: "deadlock", 1020: "deadlock", 1205: "timeout", 2002: "connection", 2003: "connection", 2006: "connection", 2013: "connection"},
    "oracle": {1: "duplicate", 60: "deadlock", 30006: "timeout", 54: "timeout", 3113: "connection", 3114: "connection", 12170: "connection", 12541: "connection"},
    "mssql": {2627: "duplicate", 2601: "duplicate", 1205: "deadlock", -2: "timeout", 10053: "connection", 10054: "connection", 10060: "connection"},
}
_TABLES["mariadb"] = _TABLES["mysql"]


def classify_error(dialect, code):
    if dialect == "sqlite":
        text = str(code)
        if "UNIQUE" in text:
            return "duplicate"
        return "timeout" if "locked" in text else "other"
    if dialect not in _TABLES:
        raise ValueError(f"dialeto desconhecido: {dialect!r}")
    if dialect == "postgresql" and str(code).startswith("08"):
        return "connection"
    return _TABLES[dialect].get(code, "other")


def is_retryable(category):
    if category not in CATEGORIES:
        raise ValueError(f"categoria desconhecida: {category!r}")
    return category in ("deadlock", "timeout", "connection")
