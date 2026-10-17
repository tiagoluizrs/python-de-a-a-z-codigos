"""Gabarito do exercício 2."""
import pandas as pd


def _paid(orders):
    return orders[orders["status"] == "paid"]


def product_report(orders):
    report = (
        _paid(orders).groupby("product")
        .agg(orders=("order_id", "count"), units=("qty", "sum"), revenue=("total", "sum"))
        .reset_index()
        .sort_values(["revenue", "product"], ascending=[False, True])
        .set_index("product")
    )
    report["share"] = report["revenue"] / report["revenue"].sum()
    return report


def monthly_revenue(orders):
    paid = _paid(orders)
    monthly = paid.set_index("date")["total"].resample("MS").sum()
    return monthly.astype("float64")


def top_customers(orders, n):
    report = (
        _paid(orders).groupby("customer_id")
        .agg(revenue=("total", "sum"), orders=("order_id", "count"))
        .reset_index()
        .sort_values(["revenue", "customer_id"], ascending=[False, True])
        .head(n)
        .reset_index(drop=True)
    )
    return report[["customer_id", "revenue", "orders"]]
