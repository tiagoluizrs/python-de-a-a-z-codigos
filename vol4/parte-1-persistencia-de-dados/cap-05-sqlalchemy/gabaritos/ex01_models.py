"""Gabarito do exercício 1."""
import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def build_models():
    class Base(DeclarativeBase):
        pass

    class Customer(Base):
        __tablename__ = "customer"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(60))
        email: Mapped[str] = mapped_column(String(120), unique=True)
        orders: Mapped[list["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan", order_by="Order.id")

    class Order(Base):
        __tablename__ = "customer_order"
        id: Mapped[int] = mapped_column(primary_key=True)
        customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
        created_at: Mapped[dt.datetime] = mapped_column(sa.DateTime, default=lambda: dt.datetime.now(dt.UTC).replace(tzinfo=None))
        customer: Mapped[Customer] = relationship(back_populates="orders")
        lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan", order_by="OrderLine.id")

        @property
        def total(self):
            return sum((line.subtotal for line in self.lines), Decimal("0.00"))

    class OrderLine(Base):
        __tablename__ = "order_line"
        __table_args__ = (CheckConstraint("quantity > 0"),)
        id: Mapped[int] = mapped_column(primary_key=True)
        order_id: Mapped[int] = mapped_column(ForeignKey("customer_order.id"))
        product: Mapped[str] = mapped_column(String(60))
        quantity: Mapped[int]
        unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
        order: Mapped[Order] = relationship(back_populates="lines")

        @property
        def subtotal(self):
            return self.quantity * self.unit_price

    return Base, Customer, Order, OrderLine
