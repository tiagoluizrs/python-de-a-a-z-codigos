"""Gabarito do exercício 6."""
import re

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def column_exists(conn, table, column):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT 1 AS x FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            (table, column))
        found = cursor.fetchone() is not None
    conn.commit()
    return found


def ensure_column(conn, table, column, definition):
    if not _NAME.match(table) or not _NAME.match(column):
        raise ValueError("nome inválido")
    if column_exists(conn, table, column):
        return False
    with conn.cursor() as cursor:
        cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}")
    conn.commit()
    return True
