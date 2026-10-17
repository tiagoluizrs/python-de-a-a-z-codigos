"""Gabarito do exercício 1."""


def split_customers(rows):
    customers, orders, conflicts, seen = {}, [], set(), set()
    for row in rows:
        if row["order_id"] in seen:
            raise ValueError(f"pedido duplicado: {row['order_id']}")
        seen.add(row["order_id"])
        customer = {"name": row["customer_name"], "city": row["customer_city"]}
        if row["customer_id"] in customers and customers[row["customer_id"]] != customer:
            conflicts.add(row["customer_id"])
        customers.setdefault(row["customer_id"], customer)
        orders.append({"id": row["order_id"], "customer_id": row["customer_id"], "total": row["total"]})
    if conflicts:
        raise ValueError("clientes inconsistentes: " + ", ".join(str(c) for c in sorted(conflicts)))
    return customers, orders
