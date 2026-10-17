"""Gabarito do exercício 5."""
import re

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def keyset_page(conn, table, order_columns, after=None, limit=10, columns="*"):
    order_columns = list(order_columns)
    if not order_columns or not _NAME.match(table) or not all(_NAME.match(c) for c in order_columns):
        raise ValueError("nomes inválidos")
    if not 1 <= limit <= 1000:
        raise ValueError("limit entre 1 e 1000")
    if columns != "*" and not all(c in columns for c in order_columns):
        raise ValueError("columns deve conter as colunas de ordenação")
    where, params = "", []
    if after is not None:
        if len(after) != len(order_columns):
            raise ValueError("after deve ter um valor por coluna de ordenação")
        names = ", ".join(order_columns)
        where = f" WHERE ({names}) > ({', '.join('?' * len(order_columns))})"
        params = list(after)
    sql = f"SELECT {columns} FROM {table}{where} ORDER BY {', '.join(order_columns)} LIMIT ?"
    cursor = conn.execute(sql, params + [limit + 1])
    names_out = [d[0] for d in cursor.description]
    rows = [tuple(r) for r in cursor.fetchall()]
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_key = tuple(rows[-1][names_out.index(c)] for c in order_columns) if has_more else None
    return rows, next_key
