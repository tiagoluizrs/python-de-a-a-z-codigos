"""Gabarito do exercício 3."""
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class CustomerRepository:
    def __init__(self, session, m):
        self.session, self.m = session, m

    def add(self, name, email):
        customer = self.m.Customer(name=name, email=email)
        self.session.add(customer)
        self.session.flush()
        return customer

    def get(self, customer_id):
        return self.session.get(self.m.Customer, customer_id)

    def get_by_email(self, email):
        return self.session.scalars(select(self.m.Customer).where(self.m.Customer.email == email)).first()

    def all(self):
        return list(self.session.scalars(select(self.m.Customer).order_by(self.m.Customer.id)))


class OrderRepository:
    def __init__(self, session, m):
        self.session, self.m = session, m

    def add(self, customer, lines):
        order = self.m.Order(customer=customer, lines=[self.m.OrderLine(product=p, quantity=q, unit_price=price) for p, q, price in lines])
        self.session.add(order)
        self.session.flush()
        return order

    def for_customer(self, customer_id):
        query = (select(self.m.Order).where(self.m.Order.customer_id == customer_id)
                 .options(selectinload(self.m.Order.lines)).order_by(self.m.Order.id))
        return list(self.session.scalars(query))


class UnitOfWork:
    def __init__(self, session_factory, m):
        self.session_factory, self.m = session_factory, m

    def __enter__(self):
        self.session = self.session_factory()
        self.customers = CustomerRepository(self.session, self.m)
        self.orders = OrderRepository(self.session, self.m)
        return self

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def __exit__(self, exc_type, exc, tb):
        self.session.rollback()
        self.session.close()
        return False
