"""Dados de eventos sintéticos e SUJOS (como chegam de verdade), gerados de forma determinística."""
from pathlib import Path

import numpy as np

COUNTRIES = np.array(["BR", "br", "Brasil", "AR", "CL", "US", "PT"])
PRODUCTS = np.array(["caneta", "caderno", "mochila", "mouse", "teclado", "monitor"])
PRICES = {"caneta": 2.5, "caderno": 18.9, "mochila": 120.0, "mouse": 45.0, "teclado": 89.9, "monitor": 799.0}


def make_csv(path: Path, n: int, dirty: float = 0.01, seed: int = 11, start_id: int = 1, day: str = "2026-03-01") -> Path:
    """Escreve ``n`` linhas ``event_id,user_id,ts,product,qty,price,country``. ``dirty`` é a fração de linhas problemáticas:
    preço ilegível, quantidade negativa, usuário vazio, data inválida e ``event_id`` repetido."""
    rng = np.random.default_rng(seed)
    ids = np.arange(start_id, start_id + n)
    users = rng.integers(1, 50_000, n).astype(str)
    seconds = rng.integers(0, 86_400, n)
    ts = [f"{day}T{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}" for s in seconds]
    products = PRODUCTS[rng.integers(0, len(PRODUCTS), n)]
    qty = rng.integers(1, 6, n).astype(str)
    price = np.array([f"{PRICES[p]:.2f}" for p in products], dtype=object)
    country = COUNTRIES[rng.integers(0, len(COUNTRIES), n)]
    bad = rng.random(n) < dirty
    kind = rng.integers(0, 5, n)
    price[bad & (kind == 0)] = "abc"
    qty[bad & (kind == 1)] = "-3"
    users[bad & (kind == 2)] = ""
    for i in np.flatnonzero(bad & (kind == 3)):
        ts[i] = "ontem"
    ids = ids.astype(object)
    dup = np.flatnonzero(bad & (kind == 4))
    dup = dup[dup > 0]
    ids[dup] = ids[dup - 1]                                              # event_id repetido: copia o id da linha de cima
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write("event_id,user_id,ts,product,qty,price,country\n")
        for row in zip(ids, users, ts, products, qty, price, country):
            f.write(",".join(map(str, row)) + "\n")
    return path
