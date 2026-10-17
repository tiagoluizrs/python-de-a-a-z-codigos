"""Gabarito do exercício 1."""
import polars as pl


def add_features(df):
    total = pl.col("qty") * pl.col("unit_price")
    return df.with_columns(
        total=total,
        tier=pl.when(total >= 1000).then(pl.lit("alto")).when(total >= 100).then(pl.lit("médio")).otherwise(pl.lit("baixo")),
        weekday=pl.col("date").dt.to_string("%A"),
        is_weekend=pl.col("date").dt.weekday() >= 6,
        month=pl.col("date").dt.truncate("1mo").dt.date(),
        paid_total=pl.when(pl.col("status") == "paid").then(total).otherwise(pl.lit(0.0)),
    )


def tier_counts(df):
    counts = add_features(df).group_by("tier").agg(n=pl.len()).sort(["n", "tier"], descending=[True, False])
    return dict(zip(counts["tier"].to_list(), counts["n"].to_list()))
