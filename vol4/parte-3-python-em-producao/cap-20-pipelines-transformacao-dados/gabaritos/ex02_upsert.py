"""Gabarito do exercício 2."""
import sqlite3


def make_db():
    db = sqlite3.connect(":memory:")
    db.execute("create table sales (order_id integer primary key, day text not null, total real not null, updated_at text not null)")
    return db


UPSERT = """
insert into sales (order_id, day, total, updated_at) values (:order_id, :day, :total, :updated_at)
on conflict (order_id) do update set day = excluded.day, total = excluded.total, updated_at = excluded.updated_at
where excluded.updated_at > sales.updated_at
"""


def upsert(db, rows):
    result = {"inserted": 0, "updated": 0, "ignored": 0}
    with db:
        for row in rows:
            existed = db.execute("select 1 from sales where order_id = ?", (row["order_id"],)).fetchone() is not None
            before = db.total_changes
            db.execute(UPSERT, row)
            changed = db.total_changes > before
            if not existed:
                result["inserted"] += 1
            elif changed:
                result["updated"] += 1
            else:
                result["ignored"] += 1
    return result


def replace_partition(db, day, rows):
    if any(r["day"] != day for r in rows):
        raise ValueError("todas as linhas devem ser do dia informado")
    with db:
        db.execute("delete from sales where day = ?", (day,))
        db.executemany("insert into sales (order_id, day, total, updated_at) values (:order_id, :day, :total, :updated_at)", rows)
    return db.execute("select count(*) from sales where day = ?", (day,)).fetchone()[0]


def totals_by_day(db):
    rows = db.execute("select day, count(*), round(sum(total), 2) from sales group by day order by day").fetchall()
    return {day: (n, total) for day, n, total in rows}
