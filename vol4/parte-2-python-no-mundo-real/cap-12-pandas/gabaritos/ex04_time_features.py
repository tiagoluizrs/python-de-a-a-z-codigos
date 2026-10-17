"""Gabarito do exercício 4."""
import numpy as np
import pandas as pd


def daily_revenue(orders, start=None, end=None):
    days = orders["date"].dt.floor("D")
    series = orders["total"].groupby(days).sum()
    first = pd.Timestamp(start) if start is not None else series.index.min()
    last = pd.Timestamp(end) if end is not None else series.index.max()
    full = pd.date_range(first, last, freq="D")
    result = series.reindex(full, fill_value=0.0).astype("float64")
    result.index.freq = "D"
    result.name = "revenue"
    return result


def add_trend(series, window=7):
    out = pd.DataFrame({"revenue": series})
    out["ma"] = series.rolling(window).mean()
    out["change"] = series.diff()
    previous = series.shift(1)
    out["growth"] = (series - previous) / previous.where(previous != 0, np.nan) * 100
    return out


def best_weekday(series):
    return series.groupby(series.index.day_name()).mean().idxmax()
