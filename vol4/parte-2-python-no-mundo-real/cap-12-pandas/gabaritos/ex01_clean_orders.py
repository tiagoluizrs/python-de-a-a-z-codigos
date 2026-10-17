"""Gabarito do exercício 1."""
import numpy as np
import pandas as pd

ESSENTIAL = ["order_id", "customer", "date", "amount"]


def _money(series: pd.Series) -> pd.Series:
    cleaned = (series.str.replace("R$", "", regex=False).str.strip()
               .str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    return pd.to_numeric(cleaned, errors="coerce")


def clean_orders(raw: pd.DataFrame):
    df = raw.copy()
    keys = {"Order ID": "order_id", "Customer": "customer", "Date": "date", "Amount": "amount", "Status": "status"}
    df = df.rename(columns=keys)
    df = df.drop_duplicates()                                    # duplicatas exatas saem antes de qualquer relatório
    original = raw.loc[df.index]

    df["order_id"] = pd.to_numeric(df["order_id"], errors="coerce").astype("Int64")
    df["customer"] = df["customer"].str.strip().str.title().replace("", np.nan)
    iso = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    br = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df["date"] = iso.fillna(br)
    df["amount"] = _money(df["amount"])
    df["status"] = df["status"].str.strip().str.lower()

    bad = df[ESSENTIAL].isna()
    bad["amount"] = bad["amount"] | (df["amount"] <= 0)
    rejected_mask = bad.any(axis=1)

    reasons = bad[rejected_mask].apply(lambda row: ",".join(col for col in ESSENTIAL if row[col]), axis=1)
    rejected = original[rejected_mask].assign(reason=reasons)
    clean = df[~rejected_mask].reset_index(drop=True)
    return clean[["order_id", "customer", "date", "amount", "status"]], rejected
