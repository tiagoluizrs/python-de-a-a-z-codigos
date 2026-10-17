"""Gabarito do exercício 2."""
import polars as pl


def customer_report(orders):
    paid = orders.filter(pl.col("status") == "paid")
    by_product = (
        paid.group_by("customer_id", "product").agg(rev=pl.col("total").sum())
        .sort(["customer_id", "rev", "product"], descending=[False, True, False])
        .group_by("customer_id", maintain_order=True).agg(top_product=pl.col("product").first())
    )
    return (
        paid.group_by("customer_id")
        .agg(orders=pl.len(), revenue=pl.col("total").sum(), first_order=pl.col("date").min(), last_order=pl.col("date").max())
        .join(by_product, on="customer_id", how="left")
        .sort(["revenue", "customer_id"], descending=[True, False])
    )


def share_within_product(orders):
    return orders.with_columns(
        share=pl.col("total") / pl.col("total").sum().over("product"),
        rank=pl.col("total").rank("ordinal", descending=True).over("product"),
    )
