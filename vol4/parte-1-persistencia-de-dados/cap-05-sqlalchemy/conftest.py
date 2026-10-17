"""Fixtures: carregar exercício/gabarito e engines SQLAlchemy opcionais para cada banco."""
import importlib.util
import os
import sys
from pathlib import Path

import pytest

CHAPTER_DIR = Path(__file__).parent

URLS = {
    "sqlite": "sqlite://",
    "postgresql": os.environ.get("PG_URL", "postgresql+psycopg://postgres:postgres@localhost:55432/postgres"),
    "mysql": os.environ.get("MYSQL_URL", "mysql+pymysql://root:root@127.0.0.1:53306/livro?charset=utf8mb4"),
    "mariadb": os.environ.get("MARIADB_URL", "mariadb+pymysql://root:root@127.0.0.1:53307/livro?charset=utf8mb4"),
    "oracle": os.environ.get("ORACLE_URL", "oracle+oracledb://system:oracle@localhost:51521/?service_name=FREEPDB1"),
    "mssql": os.environ.get("MSSQL_URL", "mssql+mssqlpython://sa:Livro_12345@localhost:51433/livro?Encrypt=no&TrustServerCertificate=yes"),
}


@pytest.fixture
def load_exercise():
    folder = "gabaritos" if os.environ.get("CHECK_GABARITOS") else "exercicios"

    def _load(name: str):
        path = CHAPTER_DIR / folder / f"{name}.py"
        module_name = f"{folder}_{name}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    return _load


@pytest.fixture
def sqlite_engine():
    import sqlalchemy as sa
    from sqlalchemy import event
    from sqlalchemy.pool import StaticPool

    engine = sa.create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA foreign_keys = ON")

    yield engine
    engine.dispose()


@pytest.fixture(params=list(URLS))
def any_engine(request):
    """Um engine para CADA banco disponível; os indisponíveis são pulados."""
    import sqlalchemy as sa

    engine = sa.create_engine(URLS[request.param])
    if request.param != "sqlite":
        try:
            with engine.connect():
                pass
        except Exception as error:
            engine.dispose()
            pytest.skip(f"{request.param} indisponível ({type(error).__name__}); veja o Capítulo 2 a 4")
    yield engine
    engine.dispose()
