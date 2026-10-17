import io
import pickle
import sqlite3
import zipfile
from decimal import Decimal

import pytest


# ---------- 1: safe_join ----------
def test_safe_join_accepts_inside(load_exercise, tmp_path):
    safe_join = load_exercise("ex01_safe_join").safe_join
    assert safe_join(tmp_path, "a", "b.txt") == (tmp_path / "a" / "b.txt").resolve()
    assert safe_join(tmp_path, "a/../b") == (tmp_path / "b").resolve()
    assert safe_join(tmp_path) == tmp_path.resolve()


@pytest.mark.parametrize("parts", [("..",), ("../x",), ("a/../../x",), ("/etc/passwd",), ("C:/Windows/x",), ("\\\\server\\share",),
                                   ("ok", "../../x"), ("a\0b",)])
def test_safe_join_rejects(load_exercise, tmp_path, parts):
    with pytest.raises(ValueError):
        load_exercise("ex01_safe_join").safe_join(tmp_path, *parts)


def test_safe_join_prefix_trick(load_exercise, tmp_path):
    safe_join = load_exercise("ex01_safe_join").safe_join
    base = tmp_path / "files"
    base.mkdir()
    (tmp_path / "files_secret").mkdir()
    with pytest.raises(ValueError):
        safe_join(base, "../files_secret/x")           # começa com o mesmo texto, mas é outra pasta


# ---------- 2: safe_extract_zip ----------
def make_zip(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries:
            archive.writestr(name, content)
    return path


def test_unzip_ok(load_exercise, tmp_path):
    unzip = load_exercise("ex02_safe_unzip").safe_extract_zip
    archive = make_zip(tmp_path / "a.zip", [("a/b.txt", b"hello " * 10), ("c.txt", b"data 123456"), ("d/", b"")])
    names = unzip(archive, tmp_path / "out")
    assert names == ["a/b.txt", "c.txt"] and (tmp_path / "out" / "a" / "b.txt").read_bytes() == b"hello " * 10
    assert (tmp_path / "out" / "d").is_dir()


@pytest.mark.parametrize("name", ["../evil.txt", "a/../../evil.txt", "/abs.txt", "C:/x.txt", "ok/../../../y"])
def test_unzip_rejects_escape_and_extracts_nothing(load_exercise, tmp_path, name):
    unzip = load_exercise("ex02_safe_unzip").safe_extract_zip
    archive = make_zip(tmp_path / "bad.zip", [("good.txt", b"1234567890"), (name, b"x")])
    with pytest.raises(ValueError):
        unzip(archive, tmp_path / "out")
    assert not (tmp_path / "out" / "good.txt").exists()               # nada foi extraído
    assert not (tmp_path.parent / "evil.txt").exists()


def test_unzip_limits(load_exercise, tmp_path):
    unzip = load_exercise("ex02_safe_unzip").safe_extract_zip
    bomb = make_zip(tmp_path / "bomb.zip", [("zeros.bin", b"\0" * 5_000_000)])
    with pytest.raises(ValueError):
        unzip(bomb, tmp_path / "o1")                                  # razão enorme
    many = make_zip(tmp_path / "many.zip", [(f"f{i}.txt", str(i).encode() * 5) for i in range(20)])
    with pytest.raises(ValueError):
        unzip(many, tmp_path / "o2", max_files=10)
    assert len(unzip(many, tmp_path / "o3", max_files=20)) == 20
    big = make_zip(tmp_path / "big.zip", [("a", bytes(range(256)) * 4), ("b", bytes(range(256)) * 4)])
    with pytest.raises(ValueError):
        unzip(big, tmp_path / "o4", max_total_bytes=2000, max_ratio=1000)
    assert unzip(bomb, tmp_path / "o5", max_ratio=10_000_000, max_total_bytes=10_000_000) == ["zeros.bin"]


# ---------- 3: restricted_loads ----------
class Evil:
    def __reduce__(self):
        import os
        return (os.system, ("echo nunca",))


def test_restricted_loads_plain_data(load_exercise):
    loads = load_exercise("ex03_restricted_pickle").restricted_loads
    data = {"a": [1, 2.5, "x", None, True], "b": (1, 2), "c": b"raw"}
    assert loads(pickle.dumps(data)) == data


def test_restricted_loads_blocks_payloads(load_exercise):
    module = load_exercise("ex03_restricted_pickle")
    with pytest.raises(pickle.UnpicklingError, match="proibido: (nt|posix|os)\\.system"):
        module.restricted_loads(pickle.dumps(Evil()))

    class Printer:
        def __reduce__(self):
            return (print, ("x",))

    with pytest.raises(pickle.UnpicklingError, match="proibido: builtins.print"):
        module.restricted_loads(pickle.dumps(Printer()))


def test_restricted_loads_allowlist(load_exercise):
    loads = load_exercise("ex03_restricted_pickle").restricted_loads
    raw = pickle.dumps({"d": Decimal("1.5"), "s": {1, 2}})
    with pytest.raises(pickle.UnpicklingError):
        loads(raw)
    assert loads(raw, {("decimal", "Decimal"), ("builtins", "set")}) == {"d": Decimal("1.5"), "s": {1, 2}}


# ---------- 4: passwords ----------
FAST = dict(n=2**4, r=8, p=1)


def test_hash_password_format_and_salt(load_exercise):
    m = load_exercise("ex04_passwords")
    one, two = m.hash_password("segredo", **FAST), m.hash_password("segredo", **FAST)
    assert one != two and one.startswith("scrypt$16$8$1$")
    prefix, n, r, p, salt, digest = one.split("$")
    assert len(bytes.fromhex(salt)) == 16 and len(bytes.fromhex(digest)) == 32


def test_verify_password(load_exercise):
    m = load_exercise("ex04_passwords")
    stored = m.hash_password("correto cavalo", **FAST)
    assert m.verify_password("correto cavalo", stored) is True
    assert m.verify_password("errado", stored) is False and m.verify_password("", stored) is False
    assert m.verify_password("ação ç", m.hash_password("ação ç", **FAST)) is True


@pytest.mark.parametrize("bad", ["", "abc", "scrypt$1$2", "bcrypt$16$8$1$aa$bb", "scrypt$x$8$1$aa$bb", "scrypt$16$8$1$zz$bb",
                                 "scrypt$16$8$1$00$00$extra"])
def test_verify_password_malformed(load_exercise, bad):
    assert load_exercise("ex04_passwords").verify_password("x", bad) is False


def test_needs_rehash(load_exercise):
    m = load_exercise("ex04_passwords")
    weak = m.hash_password("x", n=2**4, r=8, p=1)
    assert m.needs_rehash(weak, n=2**5, r=8, p=1) is True and m.needs_rehash(weak, n=2**4, r=8, p=1) is False
    assert m.needs_rehash(weak, n=2**4, r=16, p=1) is True and m.needs_rehash("lixo") is True
    assert m.needs_rehash(m.hash_password("x", n=2**6, r=8, p=1), n=2**5, r=8, p=1) is False


# ---------- 5: safe_eval ----------
@pytest.mark.parametrize("expression, expected", [("1 + 2 * 3", 7), ("(1 + 2) * 3", 9), ("-2 ** 2", -4), ("2 ** -1", 0.5), ("7 // 2 + 7 % 2", 4),
                                                  ("10 / 4", 2.5), ("+3", 3), (" 4 * (2 + 3) - 1 ", 19), ("1.5 * 2", 3.0), ("2 ** 100", 2 ** 100)])
def test_safe_eval_values(load_exercise, expression, expected):
    assert load_exercise("ex05_safe_eval").safe_eval(expression) == expected


@pytest.mark.parametrize("expression", ["__import__('os').system('x')", "abs(1)", "a + 1", "'a' * 3", "[1]", "(lambda: 1)()", "1 < 2", "True + 1",
                                        "1 +", "", "2 ** 101", "9 ** 9 ** 9", "x.y", "1 if 1 else 2", "1; 2", "'a'", "None"])
def test_safe_eval_rejects(load_exercise, expression):
    with pytest.raises(ValueError):
        load_exercise("ex05_safe_eval").safe_eval(expression)


def test_safe_eval_limits_and_zero(load_exercise):
    safe_eval = load_exercise("ex05_safe_eval").safe_eval
    with pytest.raises(ValueError):
        safe_eval("1" * 101)
    with pytest.raises(ValueError):
        safe_eval("1 + 1 + 1", max_length=5)
    assert safe_eval("2 ** 8", max_exponent=8) == 256
    with pytest.raises(ZeroDivisionError):
        safe_eval("1 / 0")


# ---------- 6: select_where ----------
@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT, role TEXT, boss INTEGER)")
    conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", [(1, "ana", "user", None), (2, "bia", "admin", 1), (3, "caio", "user", 1),
                                                              (4, "x' OR '1'='1", "user", 2)])
    conn.execute("CREATE TABLE secrets (v TEXT)")
    return conn


ALLOWED = {"users": {"id", "name", "role", "boss"}}


def test_select_basic(load_exercise, db):
    select = load_exercise("ex06_safe_select").select_where
    assert select(db, "users", ALLOWED, {}) and len(select(db, "users", ALLOWED, {})) == 4
    assert select(db, "users", ALLOWED, {"role": "admin"}) == [(2, "bia", "admin", 1)]
    assert [r[0] for r in select(db, "users", ALLOWED, {"role": "user", "boss": 1})] == [3]
    assert [r[0] for r in select(db, "users", ALLOWED, {"boss": None})] == [1]
    assert [r[0] for r in select(db, "users", ALLOWED, {"id": [1, 3, 99]})] == [1, 3]
    assert select(db, "users", ALLOWED, {"id": []}) == []


def test_select_order_limit(load_exercise, db):
    select = load_exercise("ex06_safe_select").select_where
    assert [r[0] for r in select(db, "users", ALLOWED, {}, order_by="-id")] == [4, 3, 2, 1]
    assert [r[1] for r in select(db, "users", ALLOWED, {}, order_by="name", limit=2)] == ["ana", "bia"]
    assert select(db, "users", ALLOWED, {}, limit=0) == []


def test_select_blocks_injection(load_exercise, db):
    select = load_exercise("ex06_safe_select").select_where
    assert [r[0] for r in select(db, "users", ALLOWED, {"name": "x' OR '1'='1"})] == [4]      # o valor é só um valor
    for call in (lambda: select(db, "secrets", ALLOWED, {}), lambda: select(db, "users; DROP TABLE users", ALLOWED, {}),
                 lambda: select(db, "users", ALLOWED, {"1=1 --": 1}), lambda: select(db, "users", ALLOWED, {}, order_by="id; DROP TABLE users"),
                 lambda: select(db, "users", ALLOWED, {}, order_by="-nope"), lambda: select(db, "users", ALLOWED, {}, limit=-1),
                 lambda: select(db, "users", ALLOWED, {}, limit=True), lambda: select(db, "users", ALLOWED, {}, limit="1; DROP")):
        with pytest.raises(ValueError):
            call()
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 4
