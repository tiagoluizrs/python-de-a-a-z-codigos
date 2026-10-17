"""Gabarito do exercício 3."""
import itertools
import re

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def bulk_insert(conn, table, columns, rows, batch_size=1000):
    columns = list(columns)
    if not _NAME.match(table) or not columns or not all(_NAME.match(c) for c in columns):
        raise ValueError("nome de tabela ou coluna inválido")
    if batch_size < 1:
        raise ValueError("batch_size >= 1")
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})"
    iterator = iter(rows)
    total = 0
    with conn:
        while batch := list(itertools.islice(iterator, batch_size)):
            conn.executemany(sql, batch)
            total += len(batch)
    return total
