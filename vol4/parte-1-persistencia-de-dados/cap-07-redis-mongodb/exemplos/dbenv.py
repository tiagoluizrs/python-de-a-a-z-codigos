"""Endereços dos servidores (Capítulo 12 do Volume 3: configuração por ambiente)."""
import os

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:56379/15")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:57017/?directConnection=true")
