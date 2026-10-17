"""Gabarito do exercício 4."""
import sqlite3

SCHEMA = """
create table orders (id integer primary key, total integer not null);
create table outbox (id integer primary key autoincrement, topic text not null, body text not null, published integer not null default 0);
"""


def make_db():
    db = sqlite3.connect(":memory:")
    db.executescript(SCHEMA)
    return db


def place_order(db, order_id, total):
    if total < 0:
        raise ValueError("total negativo")
    with db:
        db.execute("insert into orders values (?, ?)", (order_id, total))
        db.execute("insert into outbox (topic, body) values ('order_created', ?)", (str(order_id),))


def pending(db):
    return db.execute("select count(*) from outbox where published = 0").fetchone()[0]


def relay(db, publish, batch=100):
    sent = failed = 0
    rows = db.execute("select id, topic, body from outbox where published = 0 order by id limit ?", (batch,)).fetchall()
    for row_id, topic, body in rows:
        try:
            publish(topic, body)
        except ConnectionError:
            failed = 1
            break
        with db:
            db.execute("update outbox set published = 1 where id = ?", (row_id,))
        sent += 1
    return {"sent": sent, "failed": failed, "pending": pending(db)}


def drain(db, publish, max_rounds=50):
    rounds = 0
    while pending(db) and rounds < max_rounds:
        relay(db, publish)
        rounds += 1
    return rounds
