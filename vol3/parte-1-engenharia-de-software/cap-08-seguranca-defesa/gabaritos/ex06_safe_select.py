"""Gabarito do exercício 6."""


def select_where(conn, table, allowed, filters, order_by=None, limit=None):
    if table not in allowed:
        raise ValueError(f"tabela não permitida: {table!r}")
    columns = allowed[table]
    clauses, params = [], []
    for column, value in filters.items():
        if column not in columns:
            raise ValueError(f"coluna não permitida: {column!r}")
        if value is None:
            clauses.append(f"{column} IS NULL")
        elif isinstance(value, (list, tuple)):
            if not value:
                clauses.append("1 = 0")
            else:
                clauses.append(f"{column} IN ({', '.join('?' * len(value))})")
                params.extend(value)
        else:
            clauses.append(f"{column} = ?")
            params.append(value)
    sql = f"SELECT * FROM {table}"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    if order_by is not None:
        descending = order_by.startswith("-")
        column = order_by[1:] if descending else order_by
        if column not in columns:
            raise ValueError(f"coluna não permitida: {column!r}")
        sql += f" ORDER BY {column}" + (" DESC" if descending else "")
    if limit is not None:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            raise ValueError("limit inválido")
        sql += " LIMIT ?"
        params.append(limit)
    return conn.execute(sql, params).fetchall()
