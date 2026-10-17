"""Gabarito do exercício 5."""
import pandas as pd
from pandas.api import types as pdt


def slim(df, max_unique_ratio=0.5):
    out = df.copy()
    for name in out.columns:
        col = out[name]
        if pdt.is_bool_dtype(col):
            continue
        if pdt.is_integer_dtype(col):
            downcast = "unsigned" if (col >= 0).all() else "integer"
            out[name] = pd.to_numeric(col, downcast=downcast)
        elif pdt.is_float_dtype(col) and col.dtype == "float64":
            small = col.astype("float32")
            if small.astype("float64").equals(col):
                out[name] = small
        elif pdt.is_string_dtype(col) or col.dtype == object:
            if len(col) and col.nunique() / len(col) < max_unique_ratio:
                out[name] = col.astype("category")
    return out


def savings(before, after):
    b = int(before.memory_usage(deep=True).sum())
    a = int(after.memory_usage(deep=True).sum())
    return {"before": b, "after": a, "ratio": round(b / a, 2)}
