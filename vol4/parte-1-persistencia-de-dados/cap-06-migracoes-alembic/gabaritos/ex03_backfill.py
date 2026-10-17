"""Gabarito do exercício 3."""
import re

import sqlalchemy as sa

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def plan_add_required_column(table, column, column_type, fill_expression):
    if not _NAME.match(table) or not _NAME.match(column):
        raise ValueError("nome inválido")
    return [
        f"ALTER TABLE {table} ADD COLUMN {column} {column_type} NULL",
        f"UPDATE {table} SET {column} = {fill_expression} WHERE {column} IS NULL",
        f"ALTER TABLE {table} ALTER COLUMN {column} SET NOT NULL",
    ]


def backfill(conn, table, column, value, batch_size=1000, id_column="id"):
    if batch_size < 1 or not all(_NAME.match(n) for n in (table, column, id_column)):
        raise ValueError("batch_size >= 1 e nomes válidos")
    top = conn.execute(sa.text(f"SELECT MAX({id_column}) FROM {table}")).scalar()
    conn.commit()
    if top is None:
        return 0
    batches = 0
    for low in range(0, top + 1, batch_size):
        conn.execute(
            sa.text(f"UPDATE {table} SET {column} = :value WHERE {id_column} >= :low AND {id_column} < :high AND {column} IS NULL"),
            {"value": value, "low": low, "high": low + batch_size})
        conn.commit()
        batches += 1
    return batches
