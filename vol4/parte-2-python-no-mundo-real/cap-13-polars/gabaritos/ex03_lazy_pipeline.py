"""Gabarito do exercício 3."""
import polars as pl


def monthly_revenue_query(path):
    return (
        pl.scan_parquet(path)
        .filter(pl.col("status") == "paid")
        .with_columns(month=pl.col("date").dt.truncate("1mo").dt.date())
        .group_by("month")
        .agg(revenue=pl.col("total").sum(), orders=pl.len())
        .sort("month")
    )


def run(path):
    return monthly_revenue_query(path).collect()


def explain_text(path):
    return monthly_revenue_query(path).explain()
