"""O adaptador de produção para o repositório: SQLite. O núcleo não sabe que ele existe."""
import json
import sqlite3
from decimal import Decimal

from loja.domain.money import Money
from loja.domain.order import Coupon, Order, OrderLine

SCHEMA = """
create table if not exists orders (
    id text primary key, customer_id text not null, status text not null, coupon text, lines text not null
) strict;
create index if not exists orders_customer on orders (customer_id);
"""


class SqliteOrderRepository:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.executescript(SCHEMA)

    def add(self, order: Order) -> None:
        lines = json.dumps([[l.sku, l.qty, str(l.unit_price.amount)] for l in order.lines])
        coupon = json.dumps([order.coupon.code, str(order.coupon.percent)]) if order.coupon else None
        with self.conn:
            self.conn.execute("insert into orders values (?, ?, ?, ?, ?)", (order.id, order.customer_id, order.status, coupon, lines))

    def _row_to_order(self, row) -> Order:
        id_, customer, status, coupon, lines = row
        parsed = [OrderLine(sku, qty, Money(price)) for sku, qty, price in json.loads(lines)]
        parsed_coupon = None
        if coupon:
            code, percent = json.loads(coupon)
            parsed_coupon = Coupon(code, Decimal(percent))
        return Order(id=id_, customer_id=customer, lines=parsed, coupon=parsed_coupon, status=status)

    def get(self, order_id: str) -> Order | None:
        row = self.conn.execute("select id, customer_id, status, coupon, lines from orders where id = ?", (order_id,)).fetchone()
        return self._row_to_order(row) if row else None

    def list_for_customer(self, customer_id: str) -> list[Order]:
        rows = self.conn.execute("select id, customer_id, status, coupon, lines from orders where customer_id = ? order by rowid", (customer_id,))
        return [self._row_to_order(r) for r in rows]
