import threading
from decimal import Decimal
from pathlib import Path

import pytest

import archtools
from loja.adapters.memory import FakeGateway, MemoryInventory, MemoryOrderRepository, RecordingNotifier, StaticPrices
from loja.adapters.sqlite import SqliteOrderRepository
from loja.bootstrap import CATALOG, STOCK, build
from loja.domain.money import Money
from loja.domain.order import DomainError
from loja.entrypoints import cli
from loja.services.place_order import PaymentDeclined, PlaceOrder, PlaceOrderCommand

PACKAGE = Path(__file__).parent.parent / "exemplos" / "loja"


# ---------- o pacote de exemplo: arquitetura fiscalizada por teste ----------
def test_dependency_rule_holds_in_the_example_package():
    graph = archtools.import_graph(PACKAGE)
    layers = ["domain", "ports", "services", "adapters", "entrypoints"]
    assert archtools.violations(graph, layers) == []
    assert archtools.cycles(graph) == []
    for module, deps in graph.items():
        if module.startswith("loja.domain"):
            assert all(d.startswith("loja.domain") for d in deps), f"{module} depende de fora do domínio: {deps}"


def test_domain_imports_no_infrastructure():
    import ast
    forbidden = {"sqlite3", "httpx", "smtplib", "requests", "os", "sys", "argparse", "json", "http"}
    for file in (PACKAGE / "domain").glob("*.py"):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        assert not (names & forbidden), f"{file.name} importa {names & forbidden}"


def make_use_case(repo=None, gateway=None, stock=None):
    notifier = RecordingNotifier()
    inventory = MemoryInventory(stock or STOCK)
    use_case = PlaceOrder(repo or MemoryOrderRepository(), gateway or FakeGateway(), inventory, StaticPrices(CATALOG), notifier)
    return use_case, notifier, inventory


def test_place_order_happy_path():
    repo = MemoryOrderRepository()
    use_case, notifier, inventory = make_use_case(repo)
    order = use_case(PlaceOrderCommand("ana", (("CANETA", 4), ("CADERNO", 2)), "VIP10", Decimal("0.10")))
    assert order.total() == Money("43.02") and order.status == "placed"
    assert repo.get(order.id) is order and inventory.available("CANETA") == 496
    assert notifier.sent == [("ana", "Pedido confirmado", f"{order.id}: R$ 43,02")]


@pytest.mark.parametrize("items,coupon,message", [
    ((("CANETA", 30),), None, "no máximo 20"), ((("CANETA", 1),), None, "pedido mínimo"), ((("CANETA", 0),), None, "quantidade"),
    ((("MONITOR", 6),), None, "sem estoque"), ((("CADERNO", 2),), 0.9, "cupom"),
])
def test_business_rules_reject_without_side_effects(items, coupon, message):
    repo = MemoryOrderRepository()
    gateway = FakeGateway()
    use_case, notifier, inventory = make_use_case(repo, gateway)
    cmd = PlaceOrderCommand("ana", items, "X" if coupon else None, Decimal(str(coupon)) if coupon else None)
    with pytest.raises(DomainError, match=message):
        use_case(cmd)
    assert gateway.charges == [] and repo.list_for_customer("ana") == [] and notifier.sent == []      # nada aconteceu


def test_payment_declined_does_not_persist_or_reserve():
    repo = MemoryOrderRepository()
    use_case, notifier, inventory = make_use_case(repo, FakeGateway(limit=Money("100")))
    with pytest.raises(PaymentDeclined, match="limite excedido"):
        use_case(PlaceOrderCommand("ana", (("MOCHILA", 2),)))
    assert repo.list_for_customer("ana") == [] and inventory.available("MOCHILA") == 30 and notifier.sent == []


def test_memory_and_sqlite_repositories_are_interchangeable():
    cmd = PlaceOrderCommand("ana", (("CANETA", 4), ("CADERNO", 2)), "VIP10", Decimal("0.10"))
    results = []
    for repo in (MemoryOrderRepository(), SqliteOrderRepository(":memory:")):
        use_case, _, _ = make_use_case(repo)
        order = use_case(cmd)
        loaded = repo.get(order.id)
        results.append((loaded.total(), [(l.sku, l.qty, l.unit_price) for l in loaded.lines], loaded.coupon.percent, loaded.status))
        assert [o.id for o in repo.list_for_customer("ana")] == [order.id] and repo.get("nao-existe") is None
    assert results[0] == results[1]


def test_composition_root_and_cli(capsys, tmp_path):
    use_case, repo, _ = build({"LOJA_REPO": "sqlite", "LOJA_DB": str(tmp_path / "l.db")})
    order = use_case(PlaceOrderCommand("bia", (("MOCHILA", 1),)))
    assert SqliteOrderRepository(str(tmp_path / "l.db")).get(order.id).total() == Money("120.00")
    assert cli.main(["ana", "CANETA:4", "CADERNO:2", "--coupon", "VIP10=0.10"], env={}) == 0
    assert "R$ 43,02" in capsys.readouterr().out
    assert cli.main(["ana", "CANETA:30"], env={}) == 1
    assert "no máximo 20" in capsys.readouterr().err


# ---------- ex01 ----------
def test_money(load_exercise):
    m = load_exercise("ex01_domain")
    assert m.Money("2.675").amount == Decimal("2.68") and m.Money("2.665").amount == Decimal("2.66") and m.Money(10).amount == Decimal("10.00")
    assert m.Money("1.10") + m.Money("2.20") == m.Money("3.30") and m.Money("5") - m.Money("1.5") == m.Money("3.50")
    assert m.Money("2.50") * 3 == 3 * m.Money("2.50") == m.Money("7.50") and m.Money("10") * Decimal("0.15") == m.Money("1.50")
    assert m.Money("1") < m.Money("2") <= m.Money("2") and m.Money("3") > m.Money("2") >= m.Money("2")
    assert hash(m.Money("1.0")) == hash(m.Money("1.00")) and len({m.Money("1"), m.Money("1.00")}) == 1
    assert str(m.Money("1234.5")) == "R$ 1.234,50" and repr(m.Money("1234.5")) == "Money('1234.50')" and str(m.Money(0)) == "R$ 0,00"
    with pytest.raises(TypeError):
        m.Money(1.1)
    with pytest.raises(TypeError):
        m.Money(1) * 1.5


def test_cart_add_remove(load_exercise):
    m = load_exercise("ex01_domain")
    cart = m.Cart()
    cart.add("A", 2, m.Money("5"))
    cart.add("A", 3, m.Money("6"))
    assert cart.items["A"] == (5, m.Money("6")) and cart.subtotal() == m.Money("30")
    for bad in (0, -1, 1.5, True):
        with pytest.raises(m.DomainError):
            cart.add("B", bad, m.Money("1"))
    with pytest.raises(m.DomainError, match="10 unidades"):
        cart.add("A", 6, m.Money("6"))
    cart.add("B", 10, m.Money("1"))
    cart.add("C", 10, m.Money("1"))
    with pytest.raises(m.DomainError, match="30 unidades"):
        cart.add("D", 6, m.Money("1"))
    cart.remove("B", 4)
    assert cart.items["B"][0] == 6
    cart.remove("B", 6)
    assert "B" not in cart.items
    cart.remove("C")
    with pytest.raises(m.DomainError):
        cart.remove("C")
    with pytest.raises(m.DomainError):
        cart.remove("A", 99)


def test_cart_coupon_and_checkout(load_exercise):
    m = load_exercise("ex01_domain")
    cart = m.Cart()
    with pytest.raises(m.DomainError, match="vazio"):
        cart.checkout()
    cart.add("A", 1, m.Money("5"))
    with pytest.raises(m.DomainError, match="mínimo"):
        cart.checkout()
    cart.add("A", 3, m.Money("5"))
    for percent in (Decimal("0"), Decimal("0.31"), Decimal("-0.1")):
        with pytest.raises(m.DomainError):
            cart.apply_coupon("X", percent)
    cart.apply_coupon("VIP", Decimal("0.30"))
    with pytest.raises(m.DomainError, match="um cupom"):
        cart.apply_coupon("Y", Decimal("0.1"))
    assert cart.subtotal() == m.Money("20") and cart.total() == m.Money("14")
    cart.checkout()
    assert cart.status == "closed"
    for action in (lambda: cart.add("B", 1, m.Money("1")), lambda: cart.remove("A"), lambda: cart.checkout(), lambda: cart.apply_coupon("Z", Decimal("0.1"))):
        with pytest.raises(m.DomainError, match="closed"):
            action()


# ---------- ex02 ----------
class Accounts:
    def __init__(self, balances):
        self.balances, self.writes = dict(balances), []

    def balance(self, account_id):
        return self.balances[account_id]

    def set_balance(self, account_id, cents):
        self.writes.append((account_id, cents))
        self.balances[account_id] = cents


class Ledger:
    def __init__(self):
        self.entries = []

    def record(self, source, target, cents, when):
        self.entries.append((source, target, cents, when))


class Clock:
    def now(self):
        return "2026-10-13T10:00:00"


class Notifier:
    def __init__(self, fail=False):
        self.fail, self.sent = fail, []

    def send(self, account_id, text):
        if self.fail:
            raise ConnectionError("fora do ar")
        self.sent.append((account_id, text))


def test_transfer_happy_path(load_exercise):
    m = load_exercise("ex02_use_case")
    accounts, ledger, notifier = Accounts({"a": 1000, "b": 50}), Ledger(), Notifier()
    result = m.transfer_money(accounts, ledger, notifier, Clock(), "a", "b", 300)
    assert result == m.Transfer("a", "b", 300) and accounts.balances == {"a": 700, "b": 350}
    assert ledger.entries == [("a", "b", 300, "2026-10-13T10:00:00")] and notifier.sent == [("a", "enviou 300"), ("b", "recebeu 300")]


@pytest.mark.parametrize("source,target,cents,message", [("a", "b", 0, "positivo"), ("a", "b", -5, "positivo"), ("a", "a", 10, "iguais"),
                                                           ("a", "x", 10, "conta inexistente: x"), ("x", "b", 10, "conta inexistente: x"),
                                                           ("b", "a", 999, "saldo insuficiente")])
def test_transfer_rejections_change_nothing(load_exercise, source, target, cents, message):
    m = load_exercise("ex02_use_case")
    accounts, ledger, notifier = Accounts({"a": 1000, "b": 50}), Ledger(), Notifier()
    with pytest.raises(m.TransferError, match=message):
        m.transfer_money(accounts, ledger, notifier, Clock(), source, target, cents)
    assert accounts.writes == [] and ledger.entries == [] and notifier.sent == []


def test_transfer_survives_notification_failure(load_exercise):
    m = load_exercise("ex02_use_case")
    accounts, ledger = Accounts({"a": 100, "b": 0}), Ledger()
    result = m.transfer_money(accounts, ledger, Notifier(fail=True), Clock(), "a", "b", 40)
    assert result.cents == 40 and accounts.balances == {"a": 60, "b": 40} and len(ledger.entries) == 1


# ---------- ex03 ----------
SOURCES = {
    "loja.domain.order": "from loja.domain import money\nimport os\n",
    "loja.domain.money": "",
    "loja.ports": "from loja.domain.order import Order\n",
    "loja.services.checkout": "from ..domain import order\nfrom .. import ports\nfrom loja.adapters.memory import Repo\n",
    "loja.adapters.memory": "from loja.ports import X\nimport sqlite3\n",
    "loja.bootstrap": "from loja.adapters import memory\nfrom loja.services.checkout import run\n",
}


def test_imports_of(load_exercise):
    m = load_exercise("ex03_layers")
    assert m.imports_of("loja.services.checkout", SOURCES["loja.services.checkout"], "loja") == {
        "loja.domain", "loja.domain.order", "loja", "loja.ports", "loja.adapters.memory", "loja.adapters.memory.Repo"}
    assert m.imports_of("loja.domain.order", SOURCES["loja.domain.order"], "loja") == {"loja.domain", "loja.domain.money"}
    assert m.imports_of("a.b", "import loja.x\nfrom os import path\nfrom loja.y import *\nimport loja.b", "loja") == {"loja.x", "loja.y", "loja.b"}
    assert m.imports_of("loja.m", "from loja.m import thing\nimport loja.m", "loja") == {"loja.m.thing"} or m.imports_of("loja.m", "from loja.m import thing\nimport loja.m", "loja") == set()


def test_layer_violations(load_exercise):
    m = load_exercise("ex03_layers")
    layers = ["domain", "ports", "services", "adapters"]
    assert m.layer_violations(SOURCES, layers, "loja") == [("loja.services.checkout", "loja.adapters.memory")]
    clean = {k: v for k, v in SOURCES.items() if k != "loja.services.checkout"}
    assert m.layer_violations(clean, layers, "loja") == []
    bad_domain = {**SOURCES, "loja.domain.money": "from loja.ports import PaymentResult\n"}
    assert ("loja.domain.money", "loja.ports") in m.layer_violations(bad_domain, layers, "loja")


def test_find_cycles(load_exercise):
    m = load_exercise("ex03_layers")
    assert m.find_cycles(SOURCES, "loja") == []
    cyc = {"p.a": "import p.b\n", "p.b": "from p import c\n", "p.c": "import p.a\nimport p.d\n", "p.d": "", "p.x": "import p.y\n", "p.y": "import p.x\n"}
    assert m.find_cycles(cyc, "p") == [["p.a", "p.b", "p.c", "p.a"], ["p.x", "p.y", "p.x"]]


# ---------- ex04 ----------
def test_decide(load_exercise):
    m = load_exercise("ex04_functional_core")
    empty = m.CartState()
    assert m.decide(empty, m.AddItem("A", 2)) == [m.ItemAdded("A", 2)]
    assert m.decide(empty, m.AddItem("A", 0)) == [m.Rejected("quantidade inválida")] and m.decide(empty, m.AddItem("A", -1))[0].reason == "quantidade inválida"
    assert m.decide(empty, m.RemoveItem("A")) == [m.Rejected("item não está no carrinho")]
    assert m.decide(empty, m.CloseCart()) == [m.Rejected("carrinho vazio")]
    filled = m.CartState((("A", 2),))
    assert m.decide(filled, m.RemoveItem("A")) == [m.ItemRemoved("A")] and m.decide(filled, m.CloseCart()) == [m.CartClosed()]
    closed = m.CartState((("A", 2),), True)
    for cmd in (m.AddItem("B", 1), m.RemoveItem("A"), m.CloseCart()):
        assert m.decide(closed, cmd) == [m.Rejected("carrinho fechado")]
    with pytest.raises(TypeError):
        m.decide(empty, "comando")


def test_evolve_and_replay(load_exercise):
    m = load_exercise("ex04_functional_core")
    state = m.evolve(m.CartState(), m.ItemAdded("B", 1))
    state = m.evolve(state, m.ItemAdded("A", 2))
    state = m.evolve(state, m.ItemAdded("B", 4))
    assert state.items == (("A", 2), ("B", 5)) and m.evolve(state, m.Rejected("x")) is state
    assert m.evolve(state, m.ItemRemoved("A")).items == (("B", 5),) and m.evolve(state, m.CartClosed()).closed is True
    assert m.replay([m.ItemAdded("B", 1), m.ItemAdded("A", 2), m.ItemRemoved("B"), m.CartClosed()]) == m.CartState((("A", 2),), True)
    with pytest.raises(TypeError):
        m.evolve(state, "evento")
    assert state == m.CartState((("A", 2), ("B", 5)))                       # o estado original não foi alterado


def test_handle_all_keeps_rejections_in_history(load_exercise):
    m = load_exercise("ex04_functional_core")
    cmds = [m.AddItem("A", 2), m.RemoveItem("Z"), m.AddItem("A", 0), m.CloseCart(), m.AddItem("B", 1)]
    state, history = m.handle_all(cmds)
    assert history == [m.ItemAdded("A", 2), m.Rejected("item não está no carrinho"), m.Rejected("quantidade inválida"), m.CartClosed(), m.Rejected("carrinho fechado")]
    assert state == m.CartState((("A", 2),), True) and m.replay(history) == state                  # o replay do histórico reproduz o estado


# ---------- ex05 ----------
def test_container_lazy_singleton_and_factory(load_exercise):
    m = load_exercise("ex05_container")
    c = m.Container()
    calls = []
    c.register("config", lambda ct: calls.append("config") or {"url": "x"})
    def make_repo(ct):
        url = ct.get("config")["url"]
        calls.append("repo")
        return ("repo", url)

    c.register("repo", make_repo)
    c.register("fresh", lambda ct: object(), singleton=False)
    assert c.built == set() and calls == []
    assert c.get("repo") == ("repo", "x") and c.get("repo") is c.get("repo") and calls == ["config", "repo"] and c.built == {"config", "repo"}
    assert c.get("fresh") is not c.get("fresh")
    with pytest.raises(m.DependencyError, match="desconhecido: nada"):
        c.get("nada")
    with pytest.raises(m.DependencyError):
        c.register("repo", lambda ct: 1)


def test_container_cycles(load_exercise):
    m = load_exercise("ex05_container")
    c = m.Container()
    c.register("a", lambda ct: ct.get("b"))
    c.register("b", lambda ct: ct.get("c"))
    c.register("c", lambda ct: ct.get("a"))
    c.register("ok", lambda ct: 42)
    with pytest.raises(m.DependencyError, match="ciclo: a -> b -> c -> a"):
        c.get("a")
    assert c.get("ok") == 42                                                 # continua utilizável
    with pytest.raises(m.DependencyError, match="ciclo: b -> c -> a -> b"):
        c.get("b")


def test_container_override(load_exercise):
    m = load_exercise("ex05_container")
    c = m.Container()
    c.register("gateway", lambda ct: "real")
    c.register("service", lambda ct: f"service({ct.get('gateway')})", singleton=False)
    assert c.get("service") == "service(real)"
    with c.override("gateway", "fake"):
        assert c.get("service") == "service(fake)"
        with c.override("gateway", "fake2"):
            assert c.get("gateway") == "fake2"
        assert c.get("gateway") == "fake"
    assert c.get("gateway") == "real" and c.get("service") == "service(real)"
    with pytest.raises(m.DependencyError):
        with c.override("nada", 1):
            pass
    with pytest.raises(RuntimeError):
        with c.override("gateway", "x"):
            raise RuntimeError("boom")
    assert c.get("gateway") == "real"


# ---------- ex06 ----------
class Base:
    pass


class Placed(Base):
    def __init__(self, n):
        self.n = n


class Other:
    pass


def test_event_bus_order_types_and_failures(load_exercise):
    m = load_exercise("ex06_events")
    bus, log = m.EventBus(), []

    def boom(event):
        raise RuntimeError("falhou")

    bus.subscribe(Placed, lambda e: log.append(("a", e.n)))
    bus.subscribe(Base, lambda e: log.append(("base", e.n)))
    bus.subscribe(Placed, boom)
    bus.subscribe(object, lambda e: log.append(("any", type(e).__name__)))
    ok = bus.publish(Placed(1))
    assert log == [("a", 1), ("base", 1), ("any", "Placed")] and ok == 3
    assert len(bus.failures) == 1 and isinstance(bus.failures[0][2], RuntimeError) and bus.failures[0][1] is boom
    assert bus.publish(Other()) == 1 and log[-1] == ("any", "Other")
    assert bus.failures is not bus.failures


def test_event_bus_duplicates_and_unsubscribe(load_exercise):
    m = load_exercise("ex06_events")
    bus, log = m.EventBus(), []

    def handler(event):
        log.append(event.n)

    bus.subscribe(Placed, handler)
    bus.subscribe(Placed, handler)
    bus.publish(Placed(1))
    assert log == [1]
    bus.unsubscribe(Placed, handler)
    bus.unsubscribe(Placed, handler)
    assert bus.publish(Placed(2)) == 0 and log == [1]


def test_event_bus_nested_publish_is_fifo(load_exercise):
    m = load_exercise("ex06_events")
    bus, log = m.EventBus(), []

    def first(event):
        log.append(("first", event.n))
        if event.n == 1:
            bus.publish(Placed(100))                               # entra na fila, não recursão
        log.append(("first-end", event.n))

    bus.subscribe(Placed, first)
    bus.subscribe(Placed, lambda e: log.append(("second", e.n)))
    total = bus.publish_all([Placed(1), Placed(2)])
    assert log == [("first", 1), ("first-end", 1), ("second", 1), ("first", 2), ("first-end", 2), ("second", 2),
                   ("first", 100), ("first-end", 100), ("second", 100)]
    assert total == 6
