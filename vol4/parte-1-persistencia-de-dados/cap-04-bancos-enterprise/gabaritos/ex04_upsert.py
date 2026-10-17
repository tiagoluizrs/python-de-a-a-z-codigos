"""Gabarito do exercício 4."""


def _q(dialect, name):
    if dialect in ("mysql", "mariadb"):
        return f"`{name}`"
    if dialect == "mssql":
        return f"[{name}]"
    return f'"{name}"' if dialect in ("sqlite", "postgresql") else name


def upsert_sql(dialect, table, key, columns):
    columns = list(columns)
    if not columns:
        raise ValueError("columns vazio")
    all_cols = [key, *columns]
    q = lambda n: _q(dialect, n)          # noqa: E731
    names = ", ".join(q(c) for c in all_cols)
    marks = ", ".join("?" for _ in all_cols)
    if dialect in ("sqlite", "postgresql"):
        sets = ", ".join(f"{q(c)} = excluded.{q(c)}" for c in columns)
        return f"INSERT INTO {q(table)} ({names}) VALUES ({marks}) ON CONFLICT ({q(key)}) DO UPDATE SET {sets}"
    if dialect in ("mysql", "mariadb"):
        sets = ", ".join(f"{q(c)} = VALUES({q(c)})" for c in columns)
        return f"INSERT INTO {q(table)} ({names}) VALUES ({marks}) ON DUPLICATE KEY UPDATE {sets}"
    if dialect in ("oracle", "mssql"):
        source = ", ".join(f"? AS {q(c)}" for c in all_cols)
        sets = ", ".join(f"t.{q(c)} = s.{q(c)}" for c in columns)
        values = ", ".join(f"s.{q(c)}" for c in all_cols)
        if dialect == "oracle":
            return (f"MERGE INTO {q(table)} t USING (SELECT {source} FROM dual) s ON (t.{q(key)} = s.{q(key)}) "
                    f"WHEN MATCHED THEN UPDATE SET {sets} WHEN NOT MATCHED THEN INSERT ({names}) VALUES ({values})")
        sets = ", ".join(f"{q(c)} = s.{q(c)}" for c in columns)
        return (f"MERGE {q(table)} AS t USING (SELECT {source}) AS s ON t.{q(key)} = s.{q(key)} "
                f"WHEN MATCHED THEN UPDATE SET {sets} WHEN NOT MATCHED THEN INSERT ({names}) VALUES ({values});")
    raise ValueError(f"dialeto desconhecido: {dialect!r}")
