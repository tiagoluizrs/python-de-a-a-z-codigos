"""Dados sintéticos e determinísticos usados em todos os exemplos (sem rede, sem arquivos externos)."""
import numpy as np
import pandas as pd

CITIES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Recife", "Porto Alegre", "Salvador", "Curitiba", "Fortaleza"]
PRODUCTS = {"caneta": 2.5, "caderno": 18.9, "mochila": 120.0, "mouse": 45.0, "teclado": 89.9, "monitor": 799.0}
STATUS = ["paid", "paid", "paid", "paid", "pending", "cancelled"]


def make_customers(n: int = 1_000, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "name": [f"Cliente {i:04d}" for i in range(1, n + 1)],
        "city": rng.choice(CITIES, n),
        "segment": rng.choice(["varejo", "atacado", "online"], n, p=[0.6, 0.15, 0.25]),
        "signup": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 600, n), unit="D"),
    })


def make_orders(n: int = 100_000, n_customers: int = 1_000, seed: int = 2) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    products = rng.choice(list(PRODUCTS), n)
    qty = rng.integers(1, 6, n)
    unit = np.array([PRODUCTS[p] for p in products])
    return pd.DataFrame({
        "order_id": np.arange(1, n + 1),
        "customer_id": rng.integers(1, n_customers + 1, n),
        "date": pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365 * 24 * 60, n), unit="min"),
        "product": products,
        "qty": qty,
        "unit_price": unit,
        "status": rng.choice(STATUS, n),
        "total": np.round(qty * unit, 2),
    })


def make_dirty_orders() -> pd.DataFrame:
    """Um pedaço de planilha como ela chega na vida real."""
    return pd.DataFrame({
        "Order ID": ["1001", "1002", "1002", "1003", "1004", "1005", None],
        "Customer": ["  Ana Souza ", "bruno LIMA", "bruno LIMA", "Carla Dias", "  ", "Eva Nunes", "Fábio Reis"],
        "Date": ["2026-03-01", "01/03/2026", "01/03/2026", "2026-03-04", "não sei", "2026-03-09", "2026-03-10"],
        "Amount": ["1.250,50", "300", "300", "R$ 89,90", "10", "abc", "75,00"],
        "Status": ["PAID", "paid", "paid", "Pending", "paid", "CANCELLED", "paid"],
    })
