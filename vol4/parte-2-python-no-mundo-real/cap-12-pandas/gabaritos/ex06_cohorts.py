"""Gabarito do exercício 6."""
import pandas as pd


def first_purchase_month(orders):
    months = orders["date"].dt.to_period("M")
    first = months.groupby(orders["customer_id"]).min().sort_index()
    first.name = "cohort"
    return first


def retention_counts(orders):
    months = orders["date"].dt.to_period("M")
    cohort = first_purchase_month(orders)
    frame = pd.DataFrame({
        "customer_id": orders["customer_id"],
        "cohort": orders["customer_id"].map(cohort),
        "month": months,
    }).drop_duplicates(["customer_id", "month"])
    frame["months_since"] = (frame["month"] - frame["cohort"]).apply(lambda offset: offset.n)
    table = frame.pivot_table(index="cohort", columns="months_since", values="customer_id", aggfunc="nunique", fill_value=0)
    table = table.astype(int).sort_index()
    table.columns = pd.Index([int(c) for c in table.columns], name="months_since")
    return table


def retention_rate(orders):
    counts = retention_counts(orders)
    return counts.div(counts[0], axis=0).round(4)
