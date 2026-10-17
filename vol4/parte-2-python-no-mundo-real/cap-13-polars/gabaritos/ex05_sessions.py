"""Gabarito do exercício 5."""
import polars as pl


def sessionize(events, gap_minutes=30):
    return (
        events.sort("user", "ts")
        .with_columns(new=(pl.col("ts").diff().over("user") > pl.duration(minutes=gap_minutes)).fill_null(True))
        .with_columns(session=pl.col("new").cum_sum().over("user").cast(pl.Int64))
        .drop("new")
    )


def session_summary(events, gap_minutes=30):
    return (
        sessionize(events, gap_minutes)
        .group_by("user", "session")
        .agg(start=pl.col("ts").min(), end=pl.col("ts").max(), events=pl.len())
        .with_columns(minutes=(pl.col("end") - pl.col("start")).dt.total_seconds() / 60)
        .sort("user", "session")
    )
