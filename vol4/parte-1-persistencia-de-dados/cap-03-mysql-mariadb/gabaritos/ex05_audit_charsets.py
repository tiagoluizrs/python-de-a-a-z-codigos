"""Gabarito do exercício 5."""


def audit_charsets(conn, schema):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME AS t, COLUMN_NAME AS c, CHARACTER_SET_NAME AS cs FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND CHARACTER_SET_NAME IS NOT NULL AND CHARACTER_SET_NAME <> 'utf8mb4' "
            "ORDER BY TABLE_NAME, COLUMN_NAME", (schema,))
        rows = cursor.fetchall()
    conn.commit()
    return sorted((r["t"], r["c"], r["cs"]) for r in rows)


def fix_statements(findings):
    seen, out = set(), []
    for table, _column, _charset in findings:
        if table not in seen:
            seen.add(table)
            out.append("ALTER TABLE `" + table.replace("`", "``") + "` CONVERT TO CHARACTER SET utf8mb4")
    return out
