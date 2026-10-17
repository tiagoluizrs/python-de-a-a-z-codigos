"""Gabarito do exercício 3."""
import itertools


def quote_identifier(name):
    if not name or "\x00" in name or len(name) > 64:
        raise ValueError("identificador inválido")
    return "`" + name.replace("`", "``") + "`"


def bulk_insert(conn, table, columns, rows, batch_size=1000):
    columns = list(columns)
    if not columns or batch_size < 1:
        raise ValueError("columns não vazio e batch_size >= 1")
    sql = f"INSERT INTO {quote_identifier(table)} ({', '.join(map(quote_identifier, columns))}) VALUES ({', '.join(['%s'] * len(columns))})"
    iterator = iter(rows)
    total = 0
    try:
        with conn.cursor() as cursor:
            while batch := list(itertools.islice(iterator, batch_size)):
                cursor.executemany(sql, batch)
                total += len(batch)
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    return total
