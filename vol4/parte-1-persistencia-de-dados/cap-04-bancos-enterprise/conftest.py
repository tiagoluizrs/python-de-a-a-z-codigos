"""Fixtures: carregar exercício/gabarito e conexões opcionais com cada banco.

Cada fixture PULA o teste se o servidor não responder (o capítulo funciona com qualquer
subconjunto dos servidores). SQLite está sempre disponível.
"""
import importlib.util
import os
import sys
import uuid
from pathlib import Path

import pytest

CHAPTER_DIR = Path(__file__).parent

ORACLE = dict(user=os.environ.get("ORACLE_USER", "system"), password=os.environ.get("ORACLE_PASSWORD", "oracle"),
              dsn=os.environ.get("ORACLE_DSN", "localhost:51521/FREEPDB1"))
MSSQL_CS = os.environ.get("MSSQL_CS", "SERVER=localhost,51433;DATABASE={db};UID=sa;PWD=Livro_12345;Encrypt=no;TrustServerCertificate=yes")
PG_DSN = os.environ.get("PG_DSN", "postgresql://postgres:postgres@localhost:55432/postgres")
MYSQL = dict(host="127.0.0.1", port=int(os.environ.get("MYSQL_PORT", "53306")), user="root", password="root")


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


class Backend:
    """Uma conexão + um nome de tabela único, com DDL e conversão de placeholders por dialeto."""

    def __init__(self, dialect, conn, converter):
        self.dialect = dialect
        self.conn = conn
        self.table = "t_" + uuid.uuid4().hex[:10]
        self._convert = converter

    def sql(self, text):
        return self._convert(text)

    def execute(self, text, params=()):
        cursor = self.conn.cursor()
        cursor.execute(self.sql(text), list(params) if self.dialect == "oracle" else tuple(params))
        return cursor

    def query(self, text, params=()):
        cursor = self.execute(text, params)
        return cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def drop(self):
        try:
            self.conn.rollback()
            self.execute(f"DROP TABLE {self.table}")
            self.conn.commit()
        except Exception:
            pass


def _numbered(text):                                   # ? -> :1, :2 (Oracle)
    out, n = [], 0
    for ch in text:
        if ch == "?":
            n += 1
            out.append(f":{n}")
        else:
            out.append(ch)
    return "".join(out)


def _make(dialect):
    if dialect == "sqlite":
        import sqlite3
        return Backend("sqlite", sqlite3.connect(":memory:"), lambda s: s)
    try:
        if dialect == "oracle":
            import oracledb
            return Backend("oracle", oracledb.connect(**ORACLE), _numbered)
        if dialect == "mssql":
            import mssql_python
            return Backend("mssql", mssql_python.connect(MSSQL_CS.format(db="livro"), autocommit=False), lambda s: s)
        if dialect == "postgresql":
            import psycopg
            return Backend("postgresql", psycopg.connect(PG_DSN, connect_timeout=3), lambda s: s.replace("?", "%s"))
        if dialect in ("mysql", "mariadb"):
            import pymysql
            port = MYSQL["port"] if dialect == "mysql" else int(os.environ.get("MARIADB_PORT", "53307"))
            conn = pymysql.connect(host=MYSQL["host"], port=port, user="root", password="root", database="livro", connect_timeout=3)
            return Backend(dialect, conn, lambda s: s.replace("?", "%s"))
    except Exception as error:
        pytest.skip(f"{dialect} indisponível ({type(error).__name__}: {str(error)[:80]}); veja o compose.yaml")


@pytest.fixture(params=["sqlite", "postgresql", "mysql", "mariadb", "oracle", "mssql"])
def backend(request):
    """Executa o teste em CADA banco disponível (os indisponíveis são pulados)."""
    b = _make(request.param)
    try:
        yield b
    finally:
        b.drop()
        b.conn.close()
