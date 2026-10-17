import datetime as dt
import types
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def world(load_exercise, sqlite_engine):
    Base, Customer, Order, OrderLine = load_exercise("ex01_models").build_models()
    Base.metadata.create_all(sqlite_engine)
    m = types.SimpleNamespace(Base=Base, Customer=Customer, Order=Order, OrderLine=OrderLine)
    return sqlite_engine, m


def seed(engine, m):
    with Session(engine) as s:
        ana, bia, caio = m.Customer(name="Ana Souza", email="ana@x.com"), m.Customer(name="Bia 100%", email="bia@x.com"), m.Customer(name="Caio", email="caio@x.com")
        ana.orders.append(m.Order(lines=[m.OrderLine(product="caneta", quantity=3, unit_price=Decimal("2.50")), m.OrderLine(product="caderno", quantity=2, unit_price=Decimal("18.90"))]))
        ana.orders.append(m.Order(lines=[m.OrderLine(product="mochila", quantity=1, unit_price=Decimal("120.00"))]))
        bia.orders.append(m.Order(lines=[m.OrderLine(product="lápis", quantity=10, unit_price=Decimal("1.00"))]))
        s.add_all([ana, bia, caio])
        s.commit()


# ---------- ex01 ----------
def test_models_basic_and_totals(world):
    engine, m = world
    seed(engine, m)
    with Session(engine) as s:
        ana = s.scalars(select(m.Customer).where(m.Customer.email == "ana@x.com")).one()
        assert [o.id for o in ana.orders] == sorted(o.id for o in ana.orders) and len(ana.orders) == 2
        assert ana.orders[0].total == Decimal("45.30") and isinstance(ana.orders[0].total, Decimal)
        assert ana.orders[0].lines[0].subtotal == Decimal("7.50") and ana.orders[0].customer is ana
        assert isinstance(ana.orders[0].created_at, dt.datetime)
        assert m.Order(lines=[]).total == Decimal("0.00")


def test_models_constraints_and_cascade(world):
    engine, m = world
    seed(engine, m)
    with Session(engine) as s:
        s.add(m.Customer(name="Outra Ana", email="ana@x.com"))
        with pytest.raises(sa.exc.IntegrityError):
            s.commit()
    with Session(engine) as s:
        order = s.scalars(select(m.Order)).first()
        s.add(m.OrderLine(order_id=order.id, product="x", quantity=0, unit_price=Decimal("1.00")))
        with pytest.raises(sa.exc.IntegrityError):
            s.commit()
    with Session(engine) as s:
        s.delete(s.scalars(select(m.Customer).where(m.Customer.email == "ana@x.com")).one())
        s.commit()
        assert s.scalar(select(sa.func.count()).select_from(m.OrderLine)) == 1            # sobrou só a da Bia (cascade)
        assert s.scalar(select(sa.func.count()).select_from(m.Order)) == 1
    assert m.Order.__tablename__ == "customer_order" and m.OrderLine.__tablename__ == "order_line"


def test_models_are_new_every_call(load_exercise):
    build = load_exercise("ex01_models").build_models
    a, b = build(), build()
    assert a[0] is not b[0] and a[1] is not b[1]


# ---------- ex02 ----------
def test_top_customers(world, load_exercise):
    engine, m = world
    seed(engine, m)
    q = load_exercise("ex02_queries")
    with Session(engine) as s:
        assert q.top_customers(s, m, 5) == [("Ana Souza", Decimal("165.30")), ("Bia 100%", Decimal("10.00"))]
        assert q.top_customers(s, m, 1) == [("Ana Souza", Decimal("165.30"))]
        with pytest.raises(ValueError):
            q.top_customers(s, m, 0)


def test_orders_with_lines_avoids_n_plus_one(world, load_exercise):
    engine, m = world
    seed(engine, m)
    q = load_exercise("ex02_queries")
    statements = []
    sa.event.listen(engine, "before_cursor_execute", lambda *a: statements.append(a[2]))
    with Session(engine) as s:
        ana_id = s.scalars(select(m.Customer.id).where(m.Customer.email == "ana@x.com")).one()
        statements.clear()
        orders = q.orders_with_lines(s, m, ana_id)
        total_lines = sum(len(o.lines) for o in orders)
        assert [len(o.lines) for o in orders] == [2, 1] and total_lines == 3
        assert len(statements) <= 2, statements


def test_search_customers(world, load_exercise):
    engine, m = world
    seed(engine, m)
    q = load_exercise("ex02_queries")
    with Session(engine) as s:
        assert [c.name for c in q.search_customers(s, m)] == ["Ana Souza", "Bia 100%", "Caio"]
        assert [c.name for c in q.search_customers(s, m, "ANA")] == ["Ana Souza"]
        assert [c.name for c in q.search_customers(s, m, "%")] == ["Bia 100%"]                      # % literal
        assert q.search_customers(s, m, "_") == []
        assert [c.name for c in q.search_customers(s, m, limit=1, offset=1)] == ["Bia 100%"]
        for kwargs in ({"limit": 0}, {"limit": 101}, {"offset": -1}):
            with pytest.raises(ValueError):
                q.search_customers(s, m, **kwargs)


# ---------- ex03 ----------
def test_unit_of_work_commit_and_rollback(world, load_exercise):
    engine, m = world
    UnitOfWork = load_exercise("ex03_unit_of_work").UnitOfWork
    factory = sessionmaker(engine)
    uow = UnitOfWork(factory, m)
    with uow:
        ana = uow.customers.add("Ana", "ana@x.com")
        order = uow.orders.add(ana, [("caneta", 2, Decimal("2.50"))])
        assert ana.id is not None and order.id is not None
        uow.commit()
    with uow:
        assert [c.email for c in uow.customers.all()] == ["ana@x.com"]
        assert uow.customers.get_by_email("ana@x.com").name == "Ana" and uow.customers.get_by_email("x") is None
        assert uow.orders.for_customer(1)[0].total == Decimal("5.00")
    with uow:
        uow.customers.add("Sem commit", "nc@x.com")
    with uow:
        assert uow.customers.get_by_email("nc@x.com") is None                     # nada foi gravado
    with pytest.raises(RuntimeError):
        with uow:
            uow.customers.add("Erro", "err@x.com")
            uow.commit()
            raise RuntimeError("falha depois do commit")
    with uow:
        assert uow.customers.get_by_email("err@x.com") is not None                 # o que foi confirmado fica


def test_unit_of_work_rollback_on_error_and_explicit_rollback(world, load_exercise):
    engine, m = world
    UnitOfWork = load_exercise("ex03_unit_of_work").UnitOfWork
    uow = UnitOfWork(sessionmaker(engine), m)
    with pytest.raises(sa.exc.IntegrityError):
        with uow:
            uow.customers.add("A", "dup@x.com")
            uow.commit()
            uow.customers.add("B", "dup@x.com")
    with uow:
        assert len(uow.customers.all()) == 1
        uow.customers.add("C", "c@x.com")
        uow.rollback()
        assert len(uow.customers.all()) == 1


# ---------- ex04 ----------
def test_query_counter(world, load_exercise):
    engine, m = world
    QueryCounter = load_exercise("ex04_bulk_and_counter").QueryCounter
    with QueryCounter(engine) as counter:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
            conn.execute(sa.text("SELECT 2"))
    assert counter.count == 2 and counter.statements == ["SELECT 1", "SELECT 2"]
    with engine.connect() as conn:
        conn.execute(sa.text("SELECT 3"))
    assert counter.count == 2                                                       # o ouvinte foi removido


def test_bulk_create_customers(world, load_exercise):
    engine, m = world
    q = load_exercise("ex04_bulk_and_counter")
    rows = [{"name": f"c{i}", "email": f"c{i}@x.com"} for i in range(2500)]
    with Session(engine) as s, q.QueryCounter(engine) as counter:
        assert q.bulk_create_customers(s, m, rows, batch_size=1000) == 2500
        assert s.scalar(select(sa.func.count()).select_from(m.Customer)) == 2500
    assert counter.count < 20                                                       # NÃO foi uma consulta por linha
    with Session(engine) as s:
        assert q.bulk_create_customers(s, m, []) == 0
        with pytest.raises(ValueError):
            q.bulk_create_customers(s, m, rows, batch_size=0)


def test_bulk_create_is_atomic(world, load_exercise):
    engine, m = world
    q = load_exercise("ex04_bulk_and_counter")
    rows = [{"name": f"c{i}", "email": f"e{i}@x.com"} for i in range(10)] + [{"name": "dup", "email": "e3@x.com"}]
    with Session(engine) as s:
        with pytest.raises(sa.exc.IntegrityError):
            q.bulk_create_customers(s, m, rows, batch_size=4)
        assert s.scalar(select(sa.func.count()).select_from(m.Customer)) == 0


# ---------- ex05 ----------
def test_make_engine_sqlite(load_exercise, tmp_path):
    make_engine = load_exercise("ex05_engine_factory").make_engine
    memory = make_engine("sqlite://")
    assert isinstance(memory.pool, sa.pool.StaticPool)
    with memory.connect() as conn:
        assert conn.execute(sa.text("PRAGMA foreign_keys")).scalar() == 1
    assert isinstance(make_engine("sqlite:///:memory:").pool, sa.pool.StaticPool)
    file_engine = make_engine(f"sqlite:///{tmp_path / 'a.db'}")
    assert isinstance(file_engine.pool, sa.pool.NullPool)
    with file_engine.connect() as conn:
        assert conn.execute(sa.text("PRAGMA foreign_keys")).scalar() == 1
    file_engine.dispose()


def test_make_engine_server_databases_and_errors(load_exercise):
    make_engine = load_exercise("ex05_engine_factory").make_engine
    for url in ("postgresql+psycopg://u:p@h/db", "mysql+pymysql://u:p@h/db", "mariadb+pymysql://u:p@h/db",
                "oracle+oracledb://u:p@h/?service_name=x", "mssql+mssqlpython://u:p@h/db"):
        engine = make_engine(url, pool_size=3, max_overflow=2)
        assert isinstance(engine.pool, sa.pool.QueuePool) and engine.pool.size() == 3 and engine.pool._max_overflow == 2
        assert engine.pool._pre_ping is True and engine.pool._recycle == 1800
    with pytest.raises(ValueError):
        make_engine("mongodb://h/db")
    with pytest.raises(ValueError):
        make_engine("postgresql+psycopg://u:p@h/db", pool_size=0)
    with pytest.raises(ValueError):
        make_engine("postgresql+psycopg://u:p@h/db", max_overflow=-1)


# ---------- ex06 ----------
def test_upsert_on_every_available_database(any_engine, load_exercise):
    from sqlalchemy import String
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    upsert = load_exercise("ex06_portable_upsert").upsert
    table = "sa_up_" + str(abs(hash(any_engine.url.drivername)) % 10_000)

    class Base(DeclarativeBase):
        pass

    class Stock(Base):
        __tablename__ = table
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
        name: Mapped[str] = mapped_column(String(50))
        qty: Mapped[int]

    Base.metadata.drop_all(any_engine)
    Base.metadata.create_all(any_engine)
    try:
        with Session(any_engine) as s:
            upsert(s, Stock, {"id": 1, "name": "caneta", "qty": 5}, "id")
            upsert(s, Stock, {"id": 2, "name": "lápis", "qty": 7}, "id")
            upsert(s, Stock, {"id": 1, "name": "caneta azul", "qty": 9}, "id")        # atualiza
            s.commit()
            rows = sorted((r.id, r.name, r.qty) for r in s.scalars(select(Stock)))
            assert rows == [(1, "caneta azul", 9), (2, "lápis", 7)]
            with pytest.raises(KeyError):
                upsert(s, Stock, {"name": "x", "qty": 1}, "id")
    finally:
        Base.metadata.drop_all(any_engine)
