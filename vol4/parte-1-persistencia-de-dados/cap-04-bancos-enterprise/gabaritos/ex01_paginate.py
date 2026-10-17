"""Gabarito do exercício 1."""
import re

DIALECTS = ("sqlite", "postgresql", "mysql", "mariadb", "oracle", "mssql")


def paginate(dialect, sql, limit, offset=0):
    if dialect not in DIALECTS:
        raise ValueError(f"dialeto desconhecido: {dialect!r}")
    if not isinstance(limit, int) or not isinstance(offset, int) or limit < 1 or offset < 0:
        raise ValueError("limit >= 1 e offset >= 0 (inteiros)")
    base = sql.rstrip().rstrip(";").rstrip()
    if dialect in ("oracle", "mssql"):
        if not re.search(r"\border\s+by\b", base, re.IGNORECASE):
            raise ValueError("este dialeto exige ORDER BY para paginar")
        return f"{base} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
    return f"{base} LIMIT {limit} OFFSET {offset}"
