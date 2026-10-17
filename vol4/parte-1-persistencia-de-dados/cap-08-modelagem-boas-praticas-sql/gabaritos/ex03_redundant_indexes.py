"""Gabarito do exercício 3."""


def redundant_indexes(conn):
    result = []
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        indexes = []
        for _seq, name, unique, origin, partial in conn.execute(f'PRAGMA index_list("{table}")').fetchall():
            if partial or name.startswith("sqlite_autoindex"):
                continue
            cols = tuple(r[2] for r in conn.execute(f'PRAGMA index_info("{name}")').fetchall())
            indexes.append((name, cols, bool(unique)))
        for name, cols, unique in indexes:
            if unique:
                continue
            covering = [(len(other_cols), other) for other, other_cols, _ in indexes
                        if other != name and other_cols[:len(cols)] == cols and (other_cols != cols or other < name)]
            if covering:
                result.append((table, name, min(covering)[1]))
    return sorted(result)
