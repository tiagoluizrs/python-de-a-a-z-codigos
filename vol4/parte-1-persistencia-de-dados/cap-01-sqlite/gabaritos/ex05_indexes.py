"""Gabarito do exercício 5."""
import re

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def uses_index(conn, sql, params=()):
    details = " ".join(row[-1] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params))
    return "USING INDEX" in details or "USING COVERING INDEX" in details or "USING INTEGER PRIMARY KEY" in details


def ensure_index(conn, table, column, unique=False):
    if not _NAME.match(table) or not _NAME.match(column):
        raise ValueError("nome inválido")
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
    if column not in columns:
        raise ValueError(f"{table}.{column} não existe")
    name = f"ix_{table}_{column}"
    exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = ?", (name,)).fetchone()
    if exists:
        return False
    conn.execute(f"CREATE {'UNIQUE ' if unique else ''}INDEX IF NOT EXISTS {name} ON {table} ({column})")
    conn.commit()
    return True
