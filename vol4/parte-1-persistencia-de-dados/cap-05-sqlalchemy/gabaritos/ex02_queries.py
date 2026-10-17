"""Gabarito do exercício 2."""
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload


def top_customers(session, m, n=3):
    if n < 1:
        raise ValueError("n >= 1")
    total = func.sum(m.OrderLine.quantity * m.OrderLine.unit_price)
    query = (select(m.Customer.name, total.label("total"))
             .join(m.Order, m.Order.customer_id == m.Customer.id)
             .join(m.OrderLine, m.OrderLine.order_id == m.Order.id)
             .group_by(m.Customer.id, m.Customer.name)
             .order_by(total.desc(), m.Customer.name).limit(n))
    return [(row.name, row.total) for row in session.execute(query)]


def orders_with_lines(session, m, customer_id):
    query = (select(m.Order).where(m.Order.customer_id == customer_id)
             .options(selectinload(m.Order.lines)).order_by(m.Order.id))
    return list(session.scalars(query))


def search_customers(session, m, name_contains=None, limit=20, offset=0):
    if not 1 <= limit <= 100 or offset < 0:
        raise ValueError("limit entre 1 e 100 e offset >= 0")
    query = select(m.Customer)
    if name_contains:
        query = query.where(m.Customer.name.icontains(name_contains, autoescape=True))
    return list(session.scalars(query.order_by(m.Customer.id).limit(limit).offset(offset)))
