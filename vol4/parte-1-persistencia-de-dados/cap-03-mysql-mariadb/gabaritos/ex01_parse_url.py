"""Gabarito do exercício 1."""
from urllib.parse import parse_qsl, unquote, urlsplit

_SCHEMES = {"mysql", "mariadb", "mysql+pymysql"}


def parse_mysql_url(url):
    parts = urlsplit(url)
    if parts.scheme not in _SCHEMES:
        raise ValueError(f"esquema não suportado: {parts.scheme!r}")
    if not parts.username:
        raise ValueError("usuário ausente")
    if not parts.hostname:
        raise ValueError("host ausente")
    database = parts.path.lstrip("/")
    if not database:
        raise ValueError("banco ausente")
    result = {
        "user": unquote(parts.username),
        "password": unquote(parts.password or ""),
        "host": parts.hostname,
        "port": parts.port or 3306,
        "database": database,
        "charset": "utf8mb4",
    }
    for key, value in parse_qsl(parts.query):
        result[key] = int(value) if value.isdigit() else value
    return result
