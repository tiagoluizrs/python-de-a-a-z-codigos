"""Fixtures: carregar exercício/gabarito e um schema temporário no PostgreSQL.

Suba o servidor com ``docker compose up -d``. Outro servidor? Defina ``PG_DSN``.
Sem servidor, os testes que dependem dele são PULADOS (e dizem por quê).
"""
import importlib.util
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest

CHAPTER_DIR = Path(__file__).parent
DSN = os.environ.get("PG_DSN", "postgresql://postgres:postgres@localhost:55432/postgres")


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
def pg():
    """Um schema novo por teste; ``pg.dsn`` aponta para ele; ``pg.connect()`` abre conexões nele."""
    import psycopg
    from psycopg.rows import dict_row

    try:
        admin = psycopg.connect(DSN, autocommit=True, connect_timeout=3)
    except psycopg.OperationalError as error:
        pytest.skip(f"PostgreSQL indisponível em {DSN} ({error}); rode: docker compose up -d")
    schema = "t_" + uuid.uuid4().hex[:10]
    admin.execute(f'CREATE SCHEMA "{schema}"')
    sep = "&" if "?" in DSN else "?"
    scoped = f"{DSN}{sep}options={quote('-c search_path=' + schema)}"

    class Env:
        dsn = scoped

        @staticmethod
        def connect(**kwargs):
            kwargs.setdefault("row_factory", dict_row)
            return psycopg.connect(scoped, **kwargs)

    try:
        yield Env
    finally:
        admin.execute(f'DROP SCHEMA "{schema}" CASCADE')
        admin.close()
