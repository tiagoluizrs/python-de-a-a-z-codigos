"""Gabarito do exercício 5."""
import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.pool import NullPool, QueuePool, StaticPool

_POOLED = {"postgresql", "mysql", "mariadb", "oracle", "mssql"}


def make_engine(url, *, echo=False, pool_size=5, max_overflow=10):
    parsed = sa.engine.make_url(url)
    backend = parsed.get_backend_name()
    if backend == "sqlite":
        if parsed.database in (None, "", ":memory:"):
            engine = sa.create_engine(url, echo=echo, poolclass=StaticPool, connect_args={"check_same_thread": False})
        else:
            engine = sa.create_engine(url, echo=echo, poolclass=NullPool)

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _record):
            dbapi_connection.execute("PRAGMA foreign_keys = ON")

        return engine
    if backend in _POOLED:
        if pool_size < 1 or max_overflow < 0:
            raise ValueError("pool_size >= 1 e max_overflow >= 0")
        return sa.create_engine(url, echo=echo, poolclass=QueuePool, pool_size=pool_size, max_overflow=max_overflow,
                                pool_pre_ping=True, pool_recycle=1800)
    raise ValueError(f"banco não suportado: {backend!r}")
