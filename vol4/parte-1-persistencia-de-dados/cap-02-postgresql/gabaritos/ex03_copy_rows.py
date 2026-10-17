"""Gabarito do exercício 3."""
from psycopg import sql


def copy_rows(conn, table, columns, rows):
    columns = list(columns)
    if not columns:
        raise ValueError("columns vazio")
    rows = list(rows)
    if not rows:
        return 0
    statement = sql.SQL("COPY {table} ({cols}) FROM STDIN").format(
        table=sql.Identifier(table), cols=sql.SQL(", ").join(map(sql.Identifier, columns)))
    count = 0
    with conn.transaction():
        with conn.cursor() as cursor, cursor.copy(statement) as writer:
            for row in rows:
                writer.write_row(row)
                count += 1
    return count
