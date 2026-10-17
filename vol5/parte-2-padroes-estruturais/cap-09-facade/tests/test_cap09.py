import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def build(m, fail_for=None, stock=None):
    inv = m.Inventory(stock or {"lapis": 10, "caderno": 2})
    pay, ship, note = m.Payments(), m.Shipping(fail_for), m.Notifications()
    return m.OrderFacade(inv, pay, ship, note), inv, pay, ship, note


def test_order_success(load_exercise):
    m = load_exercise("ex01_order_facade")
    facade, inv, pay, ship, note = build(m)
    result = facade.place_order("lapis", 3, "4111", "Rua A", "ana@x.com")
    assert result == {"payment_id": "pay-1", "tracking": "TRK-001"}
    assert inv.stock["lapis"] == 7 and inv.reserved == {} and pay.charges == {"pay-1": ("4111", 450)}
    assert ship.scheduled == [("Rua A", "lapis", 3)] and note.sent == [("ana@x.com", "pedido pay-1 enviado: TRK-001")]


def test_order_out_of_stock_and_validation(load_exercise):
    m = load_exercise("ex01_order_facade")
    facade, inv, pay, ship, note = build(m)
    with pytest.raises(m.OutOfStock):
        facade.place_order("caderno", 5, "4111", "Rua A", "a@x")
    assert inv.stock == {"lapis": 10, "caderno": 2} and pay.charges == {} and note.sent == []
    for bad in (0, -1):
        with pytest.raises(ValueError, match="quantidade inválida"):
            facade.place_order("lapis", bad, "4111", "Rua A", "a@x")
    with pytest.raises(KeyError):
        facade.place_order("borracha", 1, "4111", "Rua A", "a@x")
    assert inv.reserved == {} and inv.stock["lapis"] == 10


def test_order_payment_failure_releases(load_exercise):
    m = load_exercise("ex01_order_facade")
    facade, inv, pay, ship, note = build(m)
    with pytest.raises(m.PaymentFailed, match="cartão recusado"):
        facade.place_order("lapis", 4, "0000-1", "Rua A", "a@x")
    assert inv.stock["lapis"] == 10 and inv.reserved == {} and ship.scheduled == [] and note.sent == []


def test_order_shipping_failure_refunds_and_releases(load_exercise):
    m = load_exercise("ex01_order_facade")
    facade, inv, pay, ship, note = build(m, fail_for={"Rua B"})
    with pytest.raises(m.ShippingFailed):
        facade.place_order("lapis", 2, "4111", "Rua B", "a@x")
    assert pay.charges == {} and pay.refunds == [("4111", 300)] and inv.stock["lapis"] == 10 and inv.reserved == {} and note.sent == []
    ok = facade.place_order("lapis", 2, "4111", "Rua A", "a@x")                    # e o sistema continua funcionando
    assert ok["tracking"] == "TRK-001" and inv.stock["lapis"] == 8


# ---------- ex02 ----------
def write(path, text):
    path.write_text(text, encoding="utf-8")
    return path


def test_csv_to_json_numeric(load_exercise, tmp_path):
    m = load_exercise("ex02_function_facade")
    src = write(tmp_path / "a.csv", "nome,idade,nota,obs\nAna,30,8.5,ok\nBia,-7,-0.25,\n")
    count = m.csv_to_json(src, str(tmp_path / "a.json"))
    data = json.loads((tmp_path / "a.json").read_text(encoding="utf-8"))
    assert count == 2 and data == [{"nome": "Ana", "idade": 30, "nota": 8.5, "obs": "ok"}, {"nome": "Bia", "idade": -7, "nota": -0.25, "obs": ""}]
    raw = (tmp_path / "a.json").read_text(encoding="utf-8")
    assert raw.endswith("\n") and raw.startswith("[\n  {\n    \"nome\"")


def test_csv_to_json_options_and_ragged(load_exercise, tmp_path):
    m = load_exercise("ex02_function_facade")
    src = write(tmp_path / "b.csv", "a;b;c\n1;2\nx;y;z\n")
    assert m.csv_to_json(src, tmp_path / "b.json", delimiter=";", numeric=False) == 2
    assert json.loads((tmp_path / "b.json").read_text(encoding="utf-8")) == [{"a": "1", "b": "2", "c": ""}, {"a": "x", "b": "y", "c": "z"}]
    write(tmp_path / "ç.csv", "nome\nJoão\n")
    m.csv_to_json(tmp_path / "ç.csv", tmp_path / "ç.json")
    assert "João" in (tmp_path / "ç.json").read_text(encoding="utf-8")                # ensure_ascii=False


def test_csv_to_json_errors_are_atomic(load_exercise, tmp_path):
    m = load_exercise("ex02_function_facade")
    with pytest.raises(m.ConversionError, match="arquivo não encontrado"):
        m.csv_to_json(tmp_path / "nada.csv", tmp_path / "x.json")
    empty = write(tmp_path / "e.csv", "")
    with pytest.raises(m.ConversionError, match="csv vazio"):
        m.csv_to_json(empty, tmp_path / "e.json")
    bad = write(tmp_path / "bad.csv", "a,b\n1,2\n3,4,5\n")
    existing = write(tmp_path / "bad.json", "ORIGINAL")
    with pytest.raises(m.ConversionError, match="linha 3 tem colunas demais"):
        m.csv_to_json(bad, existing)
    assert existing.read_text(encoding="utf-8") == "ORIGINAL"
    assert not (tmp_path / "e.json").exists() and not list(tmp_path.glob("*.tmp"))


def test_csv_to_json_write_failure_cleans_up(load_exercise, tmp_path):
    m = load_exercise("ex02_function_facade")
    src = write(tmp_path / "a.csv", "a\n1\n")
    target = tmp_path / "pasta"
    target.mkdir()                                                                   # dst é uma pasta: o replace falha
    with pytest.raises(OSError):
        m.csv_to_json(src, target)
    assert not list(tmp_path.glob("*.tmp"))


# ---------- ex03 ----------
class FakeTransport:
    def __init__(self, failures=0, error=ConnectionError):
        self.failures, self.error, self.calls = failures, error, []

    def request(self, url, timeout, headers):
        self.calls.append((url, timeout, dict(headers)))
        if self.failures:
            self.failures -= 1
            raise self.error("caiu")
        return f"corpo de {url}"


def test_fetcher_defaults_and_overrides(load_exercise):
    m = load_exercise("ex03_escape_hatch")
    t = FakeTransport()
    f = m.Fetcher(t, timeout=3.0, headers={"A": "1", "B": "2"})
    assert f.get("http://x") == "corpo de http://x" and t.calls[-1] == ("http://x", 3.0, {"A": "1", "B": "2"})
    f.get("http://y", timeout=1.5, headers={"B": "9", "C": "3"})
    assert t.calls[-1] == ("http://y", 1.5, {"A": "1", "B": "9", "C": "3"})
    assert f.transport is t


def test_fetcher_retries(load_exercise):
    m = load_exercise("ex03_escape_hatch")
    t = FakeTransport(failures=2)
    f = m.Fetcher(t, retries=2)
    assert f.get("u") == "corpo de u" and len(t.calls) == 3 and f.stats == {"calls": 1, "retries": 2}
    t2 = FakeTransport(failures=5)
    f2 = m.Fetcher(t2, retries=1)
    with pytest.raises(ConnectionError):
        f2.get("u")
    assert len(t2.calls) == 2 and f2.stats == {"calls": 1, "retries": 1}
    with pytest.raises(ConnectionError):
        m.Fetcher(FakeTransport(failures=1)).get("u")                                # padrão: sem tentativas extras
    assert m.Fetcher(FakeTransport(), retries=0).stats == {"calls": 0, "retries": 0}
    t3 = FakeTransport(failures=1, error=ValueError)
    with pytest.raises(ValueError):
        m.Fetcher(t3, retries=5).get("u")
    assert len(t3.calls) == 1                                                        # outras exceções não repetem
    assert m.Fetcher(FakeTransport(failures=1)).get("u", retries=1) == "corpo de u"


def test_fetcher_validation_and_with_options(load_exercise):
    m = load_exercise("ex03_escape_hatch")
    t = FakeTransport()
    for kwargs, message in [({"timeout": 0}, "timeout inválido"), ({"timeout": -1}, "timeout inválido"), ({"retries": -1}, "retries inválido")]:
        with pytest.raises(ValueError, match=message):
            m.Fetcher(t, **kwargs)
    f = m.Fetcher(t, timeout=2.0, headers={"A": "1"}, retries=1)
    with pytest.raises(ValueError, match="timeout inválido"):
        f.get("u", timeout=0)
    with pytest.raises(ValueError, match="retries inválido"):
        f.get("u", retries=-2)
    g = f.with_options(headers={"B": "2"}, timeout=9.0)
    g.get("u")
    assert t.calls[-1] == ("u", 9.0, {"A": "1", "B": "2"})
    f.get("u")
    assert t.calls[-1] == ("u", 2.0, {"A": "1"}) and g is not f and g.transport is t
    with pytest.raises(TypeError, match="opção desconhecida: color"):
        f.with_options(color="red")
    assert f.stats["calls"] == 1 and g.stats["calls"] == 1                             # estatísticas por instância


# ---------- ex04 ----------
SOURCE = '''
class Shop:
    def buy(self, inventory, payments, sku):
        try:
            token = inventory.reserve(sku)
            payments.charge(sku)
            inventory.reserve(sku)
            self.log.info("x")
            make().go()
            items[0].run()
        except (PaymentFailed, OutOfStock):
            inventory.release(token)
        except KeyError:
            pass

    def nothing(self):
        return 1

def helper(a):
    def inner(x):
        x.hidden()
    a.call()
    return a.call()

async def go(client):
    await client.get()
'''


def test_coupling(load_exercise):
    m = load_exercise("ex04_coupling")
    result = m.coupling(SOURCE)
    assert list(result) == ["Shop.buy", "Shop.nothing", "helper", "go"]
    assert result["Shop.buy"] == ["KeyError", "OutOfStock", "PaymentFailed", "inventory.release", "inventory.reserve", "payments.charge"]
    assert result["Shop.nothing"] == [] and result["helper"] == ["a.call"] and result["go"] == ["client.get"]


def test_facade_gain_and_ranking(load_exercise):
    m = load_exercise("ex04_coupling")
    before = "def order(i, p, s):\n    i.reserve()\n    p.charge()\n    s.ship()\n"
    after = "def order(f):\n    f.place()\n"
    assert m.facade_gain(before, after, "order") == 2
    assert m.facade_gain(after, before, "order") == -2
    with pytest.raises(KeyError):
        m.facade_gain(before, after, "nope")
    ranked = m.most_coupled(SOURCE, top=2)
    assert ranked == [("Shop.buy", 6), ("go", 1)]
    assert [n for n, _ in m.most_coupled(SOURCE, top=10)] == ["Shop.buy", "go", "helper"]


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["facade_classico", "facade_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
