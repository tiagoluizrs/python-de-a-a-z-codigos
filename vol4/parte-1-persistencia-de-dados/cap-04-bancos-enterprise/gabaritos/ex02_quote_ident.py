"""Gabarito do exercício 2."""


def quote_ident(dialect, name):
    if not name or "\x00" in name or len(name) > 128:
        raise ValueError("identificador inválido")
    if dialect in ("sqlite", "postgresql", "oracle"):
        return '"' + name.replace('"', '""') + '"'
    if dialect in ("mysql", "mariadb"):
        return "`" + name.replace("`", "``") + "`"
    if dialect == "mssql":
        return "[" + name.replace("]", "]]") + "]"
    raise ValueError(f"dialeto desconhecido: {dialect!r}")
