"""URLs dos bancos opcionais (SQLAlchemy); o SQLite sempre está disponível."""
import os

URLS = {
    "sqlite": "sqlite://",
    "postgresql": os.environ.get("PG_URL", "postgresql+psycopg://postgres:postgres@localhost:55432/postgres"),
    "mysql": os.environ.get("MYSQL_URL", "mysql+pymysql://root:root@127.0.0.1:53306/livro?charset=utf8mb4"),
    "mariadb": os.environ.get("MARIADB_URL", "mariadb+pymysql://root:root@127.0.0.1:53307/livro?charset=utf8mb4"),
    "oracle": os.environ.get("ORACLE_URL", "oracle+oracledb://system:oracle@localhost:51521/?service_name=FREEPDB1"),
    "mssql": os.environ.get("MSSQL_URL", "mssql+mssqlpython://sa:Livro_12345@localhost:51433/livro?Encrypt=no&TrustServerCertificate=yes"),
}


def available_engines():
    """Devolve ``{nome: Engine}`` só dos bancos que respondem."""
    import sqlalchemy as sa

    engines = {}
    for name, url in URLS.items():
        engine = sa.create_engine(url)
        try:
            with engine.connect():
                pass
        except Exception:
            engine.dispose()
            continue
        engines[name] = engine
    return engines
