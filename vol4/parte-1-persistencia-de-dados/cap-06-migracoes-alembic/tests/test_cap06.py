import sqlalchemy as sa
import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table

from project import Project

GRAPH = {"a1": None, "b2": "a1", "c3": "b2", "d4": "b2", "m5": ("c3", "d4"), "e6": "m5"}


# ---------- ex01 ----------
def test_analyze_revisions_linear_and_merge(load_exercise):
    analyze = load_exercise("ex01_revision_graph").analyze_revisions
    assert analyze({"a": None, "b": "a", "c": "b"}) == {"bases": ["a"], "heads": ["c"], "order": ["a", "b", "c"]}
    result = analyze(GRAPH)
    assert result["bases"] == ["a1"] and result["heads"] == ["e6"] and result["order"] == ["a1", "b2", "c3", "d4", "m5", "e6"]
    assert analyze({}) == {"bases": [], "heads": [], "order": []}


def test_analyze_revisions_multiple_heads_and_errors(load_exercise):
    analyze = load_exercise("ex01_revision_graph").analyze_revisions
    two = analyze({"a": None, "b": "a", "c": "a", "z": None})
    assert two["heads"] == ["b", "c", "z"] and two["bases"] == ["a", "z"] and two["order"] == ["a", "b", "c", "z"]
    with pytest.raises(ValueError):
        analyze({"a": None, "b": "x"})
    with pytest.raises(ValueError):
        analyze({"a": "b", "b": "a"})
    with pytest.raises(ValueError):
        analyze({"a": ("b",), "b": "c", "c": "a"})


def test_upgrade_path(load_exercise):
    path = load_exercise("ex01_revision_graph").upgrade_path
    assert path(GRAPH, None, "e6") == ["a1", "b2", "c3", "d4", "m5", "e6"]
    assert path(GRAPH, "b2", "m5") == ["c3", "d4", "m5"]
    assert path(GRAPH, "c3", "m5") == ["d4", "m5"]
    assert path(GRAPH, "m5", "m5") == [] and path(GRAPH, None, "a1") == ["a1"]
    for args in (("zz", "e6"), (None, "zz")):
        with pytest.raises(ValueError):
            path(GRAPH, *args)


# ---------- ex02 ----------
def test_shop_metadata_names_are_deterministic(load_exercise):
    m = load_exercise("ex02_metadata")
    metadata = m.build_shop_metadata()
    assert set(metadata.tables) == {"customer", "orders"}
    assert m.constraint_names(metadata) == {
        "pk_customer", "uq_customer_email", "ix_customer_name",
        "pk_orders", "fk_orders_customer_id_customer", "ck_orders_total_non_negative"}


def test_shop_metadata_creates_real_tables(load_exercise):
    metadata = load_exercise("ex02_metadata").build_shop_metadata()
    engine = sa.create_engine("sqlite://")
    metadata.create_all(engine)
    insp = sa.inspect(engine)
    assert sorted(insp.get_table_names()) == ["customer", "orders"]
    assert {i["name"] for i in insp.get_indexes("customer")} >= {"ix_customer_name"}
    with engine.begin() as conn:
        conn.execute(sa.text("INSERT INTO customer (id, name, email) VALUES (1, 'a', 'a@x.com')"))
        with pytest.raises(sa.exc.IntegrityError):
            conn.execute(sa.text("INSERT INTO orders (id, customer_id, total) VALUES (1, 1, -5)"))


# ---------- ex03 ----------
def test_plan_add_required_column(load_exercise):
    plan = load_exercise("ex03_backfill").plan_add_required_column
    steps = plan("users", "domain", "VARCHAR(80)", "split_part(email, '@', 2)")
    assert steps == ["ALTER TABLE users ADD COLUMN domain VARCHAR(80) NULL",
                     "UPDATE users SET domain = split_part(email, '@', 2) WHERE domain IS NULL",
                     "ALTER TABLE users ALTER COLUMN domain SET NOT NULL"]
    for bad in (("users; DROP", "c"), ("u", "c d"), ("1u", "c")):
        with pytest.raises(ValueError):
            plan(*bad, "INT", "0")


def make_users(n):
    engine = sa.create_engine("sqlite://", poolclass=sa.pool.StaticPool)
    with engine.begin() as conn:
        conn.execute(sa.text("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, domain TEXT)"))
        conn.execute(sa.text("INSERT INTO users (id, email) VALUES (:i, :e)"), [{"i": i, "e": f"u{i}@x.com"} for i in range(1, n + 1)])
    return engine


def test_backfill_batches_and_idempotent(load_exercise):
    backfill = load_exercise("ex03_backfill").backfill
    engine = make_users(25)
    with engine.connect() as conn:
        assert backfill(conn, "users", "domain", "x.com", batch_size=10) == 3                 # ids 1..25 -> faixas 0-9, 10-19, 20-29
        assert conn.execute(sa.text("SELECT COUNT(*) FROM users WHERE domain = 'x.com'")).scalar() == 25
        conn.execute(sa.text("UPDATE users SET domain = 'outro' WHERE id = 3"))
        conn.commit()
        assert backfill(conn, "users", "domain", "x.com", batch_size=10) == 3
        assert conn.execute(sa.text("SELECT domain FROM users WHERE id = 3")).scalar() == "outro"   # não sobrescreve


def test_backfill_commits_per_batch_and_validates(load_exercise):
    backfill = load_exercise("ex03_backfill").backfill
    engine = make_users(30)
    commits = []
    sa.event.listen(engine, "commit", lambda conn: commits.append(1))
    with engine.connect() as conn:
        backfill(conn, "users", "domain", "d", batch_size=10)
    assert len(commits) >= 3                                                                 # uma transação curta por lote
    empty = sa.create_engine("sqlite://", poolclass=sa.pool.StaticPool)
    with empty.begin() as conn:
        conn.execute(sa.text("CREATE TABLE users (id INTEGER PRIMARY KEY, domain TEXT)"))
    with empty.connect() as conn:
        assert backfill(conn, "users", "domain", "d") == 0
        for kwargs in ({"batch_size": 0}, {"column": "d; DROP"}):
            args = {"table": "users", "column": "domain", "value": "d", **kwargs}
            with pytest.raises(ValueError):
                backfill(conn, **args)


# ---------- ex04 ----------
def base_metadata():
    metadata = MetaData()
    Table("person", metadata, Column("id", Integer, primary_key=True), Column("name", String(50), nullable=False))
    return metadata


def test_schema_drift_detects_changes(load_exercise):
    m = load_exercise("ex04_drift")
    metadata = base_metadata()
    engine = sa.create_engine("sqlite://", poolclass=sa.pool.StaticPool)
    metadata.create_all(engine)
    assert m.schema_drift(engine, metadata) == []
    m.assert_in_sync(engine, metadata)
    Table("person", metadata, Column("email", String(80)), extend_existing=True)
    Table("note", metadata, Column("id", Integer, primary_key=True))
    assert m.schema_drift(engine, metadata) == ["add_column:person.email", "add_table:note"]
    with pytest.raises(m.DriftError) as info:
        m.assert_in_sync(engine, metadata)
    assert info.value.differences == ["add_column:person.email", "add_table:note"] and isinstance(info.value, AssertionError)


def test_schema_drift_ignores_alembic_version_and_sees_removals(load_exercise):
    m = load_exercise("ex04_drift")
    metadata = base_metadata()
    engine = sa.create_engine("sqlite://", poolclass=sa.pool.StaticPool)
    metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(sa.text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        conn.execute(sa.text("CREATE TABLE legacy (id INTEGER PRIMARY KEY)"))
        conn.execute(sa.text("ALTER TABLE person ADD COLUMN age INTEGER"))
    assert m.schema_drift(engine, metadata) == ["remove_column:person.age", "remove_table:legacy"]


# ---------- ex05 / ex06 ----------
@pytest.fixture
def project(tmp_path):
    url = f"sqlite:///{(tmp_path / 'app.db').as_posix()}"
    p = Project(url)
    p.write_migration("0001", None, "base", 'op.create_table("person", sa.Column("id", sa.Integer, primary_key=True))', 'op.drop_table("person")')
    p.write_migration("0002", "0001", "email", 'op.add_column("person", sa.Column("email", sa.String(80)))', 'op.drop_column("person", "email")')
    p.write_migration("0003", "0002", "dados", 'op.execute("INSERT INTO person (id, email) VALUES (1, \'a@x.com\')")', 'op.execute("DELETE FROM person")')
    p.engine = sa.create_engine(url)
    yield p
    p.engine.dispose()
    p.cleanup()


def test_current_and_pending_revisions(load_exercise, project):
    m = load_exercise("ex05_runner")
    assert m.current_revision(project.engine) is None
    assert m.pending_revisions(project.config, project.engine) == ["0001", "0002", "0003"]
    project.upgrade("0002")
    assert m.current_revision(project.engine) == "0002"
    assert m.pending_revisions(project.config, project.engine) == ["0003"]
    project.upgrade("head")
    assert m.current_revision(project.engine) == "0003" and m.pending_revisions(project.config, project.engine) == []


def test_pending_revisions_rejects_multiple_heads(load_exercise, project):
    m = load_exercise("ex05_runner")
    project.write_migration("0004", "0002", "outra branch", "pass", "pass")
    with pytest.raises(RuntimeError, match="múltiplas cabeças"):
        m.pending_revisions(project.config, project.engine)


def test_render_sql_offline_and_summary(load_exercise, project):
    m = load_exercise("ex06_render_sql")
    sql = m.render_sql(project.config, "base", "head")
    assert "CREATE TABLE person" in sql and "INSERT INTO person" in sql
    summary = m.summarize_sql(sql)
    assert summary["CREATE"] >= 2 and summary["INSERT"] >= 2
    assert not sa.inspect(project.engine).get_table_names()                      # modo offline: NÃO tocou no banco
    partial = m.render_sql(project.config, "0001", "0002")
    assert "email" in partial and "CREATE TABLE person" not in partial


def test_summarize_sql_pure(load_exercise):
    summarize = load_exercise("ex06_render_sql").summarize_sql
    sql = "-- comentario\nBEGIN;\n\nCREATE TABLE a (x INT);\nCREATE TABLE b (y INT);\n-- fim\nINSERT INTO a VALUES (1);\nCOMMIT;\n"
    assert summarize(sql) == {"BEGIN": 1, "CREATE": 2, "INSERT": 1, "COMMIT": 1}
    assert summarize("") == {}
