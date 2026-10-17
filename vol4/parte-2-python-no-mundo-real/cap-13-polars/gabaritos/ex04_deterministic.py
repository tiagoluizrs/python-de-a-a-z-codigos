"""Gabarito do exercício 4."""
import polars as pl


def totals_by_key(df):
    return df.group_by("key").agg(total=pl.col("value").sum()).sort("key")


def first_seen_order(df):
    return df.group_by("key", maintain_order=True).agg(total=pl.col("value").sum())


def attach_names(df, names):
    if names["key"].is_duplicated().any():
        raise ValueError("chaves repetidas em names")
    return df.join(names, on="key", how="left", maintain_order="left")
