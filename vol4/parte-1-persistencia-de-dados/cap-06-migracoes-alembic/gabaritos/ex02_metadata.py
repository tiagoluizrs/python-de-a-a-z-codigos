"""Gabarito do exercício 2."""
import sqlalchemy as sa
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, MetaData, Numeric, String, Table

CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def build_shop_metadata():
    metadata = MetaData(naming_convention=CONVENTION)
    Table("customer", metadata,
          Column("id", Integer, primary_key=True),
          Column("name", String(60), nullable=False, index=True),
          Column("email", String(120), nullable=False, unique=True))
    Table("orders", metadata,
          Column("id", Integer, primary_key=True),
          Column("customer_id", Integer, ForeignKey("customer.id"), nullable=False),
          Column("total", Numeric(10, 2), nullable=False),
          CheckConstraint("total >= 0", name="total_non_negative"))
    return metadata


def constraint_names(metadata):
    names = set()
    for table in metadata.tables.values():
        for constraint in table.constraints:
            if constraint.name is not None:
                names.add(str(constraint.name))
        for index in table.indexes:
            if index.name is not None:
                names.add(str(index.name))
    return names
