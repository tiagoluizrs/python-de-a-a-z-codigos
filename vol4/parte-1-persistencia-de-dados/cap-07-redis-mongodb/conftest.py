"""Fixtures: carregar exercício/gabarito e conexões com Redis e MongoDB (testes pulam sem servidor)."""
import importlib.util
import os
import sys
import uuid
from pathlib import Path

import pytest

CHAPTER_DIR = Path(__file__).parent
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:56379/15")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:57017/?directConnection=true")


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
def rds():
    """Cliente Redis no banco 15, limpo antes e depois de cada teste."""
    import redis

    client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    try:
        client.ping()
    except redis.ConnectionError as error:
        pytest.skip(f"Redis indisponível em {REDIS_URL} ({error}); rode: docker compose up -d")
    client.flushdb()
    yield client
    client.flushdb()
    client.close()


@pytest.fixture
def mongo():
    """Um banco MongoDB novo (nome único) por teste, apagado no fim."""
    import pymongo

    client = pymongo.MongoClient(MONGO_URL, tz_aware=True, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except pymongo.errors.PyMongoError as error:
        pytest.skip(f"MongoDB indisponível em {MONGO_URL} ({type(error).__name__}); rode: docker compose up -d")
    name = "t_" + uuid.uuid4().hex[:10]
    yield client[name]
    client.drop_database(name)
    client.close()
