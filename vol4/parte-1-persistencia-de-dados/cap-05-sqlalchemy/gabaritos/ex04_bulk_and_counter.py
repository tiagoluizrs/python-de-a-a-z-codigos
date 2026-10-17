"""Gabarito do exercício 4."""
import itertools

from sqlalchemy import event, insert


class QueryCounter:
    def __init__(self, engine):
        self.engine = engine
        self.count = 0
        self.statements = []

    def _listener(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1
        self.statements.append(statement)

    def __enter__(self):
        event.listen(self.engine, "before_cursor_execute", self._listener)
        return self

    def __exit__(self, *exc):
        event.remove(self.engine, "before_cursor_execute", self._listener)
        return False


def bulk_create_customers(session, m, rows, batch_size=1000):
    if batch_size < 1:
        raise ValueError("batch_size >= 1")
    iterator, total = iter(rows), 0
    try:
        while batch := list(itertools.islice(iterator, batch_size)):
            session.execute(insert(m.Customer), batch)
            total += len(batch)
        session.commit()
    except BaseException:
        session.rollback()
        raise
    return total
