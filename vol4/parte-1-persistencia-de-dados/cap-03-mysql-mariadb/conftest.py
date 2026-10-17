"""Fixtures: carregar exercício/gabarito e um banco temporário no MySQL/MariaDB.

Suba os servidores com ``docker compose up -d``. ``MYSQL_PORT`` escolhe o servidor
(53306 = MySQL, o padrão; 53307 = MariaDB). Sem servidor, os testes dependentes são PULADOS.
"""
import importlib.util
import os
import sys
import uuid
from pathlib import Path

import pytest

CHAPTER_DIR = Path(__file__).parent
HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
PORT = int(os.environ.get("MYSQL_PORT", "53306"))


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
def db():
    """Um banco novo por teste. ``db.connect()`` abre conexões (PyMySQL, cursor de dicionários) nele."""
    import pymysql
    from pymysql.cursors import DictCursor

    try:
        admin = pymysql.connect(host=HOST, port=PORT, user="root", password="root", autocommit=True, connect_timeout=3)
    except pymysql.err.OperationalError as error:
        pytest.skip(f"MySQL/MariaDB indisponível em {HOST}:{PORT} ({error}); rode: docker compose up -d")
    name = "t_" + uuid.uuid4().hex[:10]
    with admin.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")

    class Env:
        database = name
        host = HOST
        port = PORT

        @staticmethod
        def connect(**kwargs):
            kwargs.setdefault("cursorclass", DictCursor)
            return pymysql.connect(host=HOST, port=PORT, user="root", password="root", database=name, charset="utf8mb4", **kwargs)

        @staticmethod
        def is_mariadb():
            with admin.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                return "mariadb" in cursor.fetchone()[0].lower()

    try:
        yield Env
    finally:
        with admin.cursor() as cursor:
            cursor.execute(f"DROP DATABASE `{name}`")
        admin.close()
