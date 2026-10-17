"""Gabarito do exercício 3."""
import pandas as pd


def enrich(orders, customers):
    duplicated = sorted(customers.loc[customers["customer_id"].duplicated(), "customer_id"].unique().tolist())
    if duplicated:
        raise ValueError(f"clientes duplicados: {duplicated}")
    return orders.merge(customers, on="customer_id", how="left", validate="many_to_one").reset_index(drop=True)


def orphan_orders(orders, customers):
    return orders[~orders["customer_id"].isin(customers["customer_id"])].reset_index(drop=True)


def customers_without_orders(orders, customers):
    return customers[~customers["customer_id"].isin(orders["customer_id"])].reset_index(drop=True)
