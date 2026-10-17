"""Gabarito do exercício 3."""


def convert_placeholders(dialect, sql):
    if dialect not in ("sqlite", "mssql", "postgresql", "mysql", "mariadb", "oracle"):
        raise ValueError(f"dialeto desconhecido: {dialect!r}")
    if dialect in ("sqlite", "mssql"):
        return sql
    out, count, in_string, i = [], 0, False, 0
    while i < len(sql):
        ch = sql[i]
        if ch == "'":
            if in_string and sql[i + 1:i + 2] == "'":
                out.append("''")
                i += 2
                continue
            in_string = not in_string
            out.append(ch)
        elif ch == "?" and not in_string:
            count += 1
            out.append(f":{count}" if dialect == "oracle" else "%s")
        elif ch == "%" and dialect != "oracle":
            out.append("%%")
        else:
            out.append(ch)
        i += 1
    return "".join(out)
