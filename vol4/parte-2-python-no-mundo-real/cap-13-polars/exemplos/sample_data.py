"""Dados sintéticos e determinísticos (os mesmos do capítulo do pandas, agora como DataFrames do Polars)."""
from datetime import datetime, timedelta

import numpy as np
import polars as pl

CITIES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Recife", "Porto Alegre", "Salvador", "Curitiba", "Fortaleza"]
PRODUCTS = {"caneta": 2.5, "caderno": 18.9, "mochila": 120.0, "mouse": 45.0, "teclado": 89.9, "monitor": 799.0}
STATUS = ["paid", "paid", "paid", "paid", "pending", "cancelled"]


def make_customers(n: int = 1_000, seed: int = 1) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    base = datetime(2024, 1, 1)
    return pl.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "name": [f"Cliente {i:04d}" for i in range(1, n + 1)],
        "city": rng.choice(CITIES, n),
        "segment": rng.choice(["varejo", "atacado", "online"], n, p=[0.6, 0.15, 0.25]),
        "signup": [base + timedelta(days=int(d)) for d in rng.integers(0, 600, n)],
    })


def make_orders(n: int = 100_000, n_customers: int = 1_000, seed: int = 2) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    products = rng.choice(list(PRODUCTS), n)
    qty = rng.integers(1, 6, n)
    unit = np.array([PRODUCTS[p] for p in products])
    minutes = rng.integers(0, 365 * 24 * 60, n).astype("timedelta64[m]")
    date = np.datetime64("2025-01-01T00:00") + minutes
    return pl.DataFrame({
        "order_id": np.arange(1, n + 1),
        "customer_id": rng.integers(1, n_customers + 1, n),
        "date": date.astype("datetime64[us]"),
        "product": products,
        "qty": qty,
        "unit_price": unit,
        "status": rng.choice(STATUS, n),
        "total": np.round(qty * unit, 2),
    })


def make_dirty_orders() -> pl.DataFrame:
    """Um pedaço de planilha como ela chega na vida real."""
    return pl.DataFrame({
        "Order ID": ["1001", "1002", "1002", "1003", "1004", "1005", None],
        "Customer": ["  Ana Souza ", "bruno LIMA", "bruno LIMA", "Carla Dias", "  ", "Eva Nunes", "Fábio Reis"],
        "Date": ["2026-03-01", "01/03/2026", "01/03/2026", "2026-03-04", "não sei", "2026-03-09", "2026-03-10"],
        "Amount": ["1.250,50", "300", "300", "R$ 89,90", "10", "abc", "75,00"],
        "Status": ["PAID", "paid", "paid", "Pending", "paid", "CANCELLED", "paid"],
    })
