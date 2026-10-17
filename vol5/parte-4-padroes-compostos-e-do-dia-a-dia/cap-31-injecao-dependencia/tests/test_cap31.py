import asyncio
import json
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
WHEN = datetime(2026, 1, 1, 12, 0)


# ---------- ex01 ----------
class Fakes:
    """Dublês de uma linha cada, todos anotando no MESMO diário (a ordem das chamadas é parte do contrato)."""

    def __init__(self, m, *, declined=False, save_error=None, mail_error=None):
        self.calls, self.saved = [], []
        self.m, self.declined, self.save_error, self.mail_error = m, declined, save_error, mail_error
        self.clock_calls = 0

    def next_id(self):
        self.calls.append(("next_id",))
        return 7

    def charge(self, customer, total):
        self.calls.append(("charge", customer, total))
        if self.declined:
            raise self.m.PaymentDeclined("cartão recusado")
        return "pay-1"

    def refund(self, payment_id):
        self.calls.append(("refund", payment_id))

    def save(self, order):
        self.calls.append(("save", dict(order)))
        if self.save_error:
            raise self.save_error
        self.saved.append(order)

    def send(self, to, subject):
        self.calls.append(("send", to, subject))
        if self.mail_error:
            raise self.mail_error

    def clock(self):
        self.clock_calls += 1
        return WHEN

    def service(self):
        class Orders:
            next_id, save = self.next_id, self.save

        class Payments:
            charge, refund = self.charge, self.refund

        class Mailer:
            send = self.send

        return self.m.CheckoutService(Orders(), Payments(), Mailer(), self.clock)


ITEMS = [("café", 2, 350), ("pão", 1, 120)]


def test_checkout_flow_and_order_of_calls(load_exercise):
    m = load_exercise("ex01_constructor_injection")
    fakes = Fakes(m)
    order = fakes.service().checkout("ana@x.com", ITEMS)
    assert [c[0] for c in fakes.calls] == ["next_id", "charge", "save", "send"]
    assert fakes.calls[1] == ("charge", "ana@x.com", 820) and fakes.calls[3] == ("send", "ana@x.com", "pedido 7 confirmado")
    assert order == {"id": 7, "customer": "ana@x.com", "total": 820, "payment_id": "pay-1", "at": WHEN, "email_sent": True}
    assert fakes.calls[2][1] == {"id": 7, "customer": "ana@x.com", "total": 820, "payment_id": "pay-1", "at": WHEN} and "email_sent" not in fakes.calls[2][1]
    assert fakes.clock_calls == 1


def test_validation_happens_before_any_collaborator(load_exercise):
    m = load_exercise("ex01_constructor_injection")
    fakes = Fakes(m)
    service = fakes.service()
    with pytest.raises(ValueError, match="carrinho vazio"):
        service.checkout("a@x", [])
    for bad in (0, -1, True, 1.5, "2"):
        with pytest.raises(ValueError, match="quantidade inválida"):
            service.checkout("a@x", [("x", bad, 100)])
    for bad in (-1, 2.5, True, "10"):
        with pytest.raises(ValueError, match="valor inválido"):
            service.checkout("a@x", [("x", 1, bad)])
    assert fakes.calls == [] and fakes.clock_calls == 0


def test_declined_payment_saves_and_sends_nothing(load_exercise):
    m = load_exercise("ex01_constructor_injection")
    fakes = Fakes(m, declined=True)
    with pytest.raises(m.PaymentDeclined, match="cartão recusado"):
        fakes.service().checkout("a@x", ITEMS)
    assert [c[0] for c in fakes.calls] == ["next_id", "charge"] and fakes.saved == []


def test_failure_after_charge_refunds(load_exercise):
    m = load_exercise("ex01_constructor_injection")
    fakes = Fakes(m, save_error=RuntimeError("disco cheio"))
    with pytest.raises(RuntimeError, match="disco cheio"):
        fakes.service().checkout("a@x", ITEMS)
    assert [c[0] for c in fakes.calls] == ["next_id", "charge", "save", "refund"] and fakes.calls[-1] == ("refund", "pay-1")


def test_mail_failure_does_not_undo_the_order(load_exercise):
    m = load_exercise("ex01_constructor_injection")
    fakes = Fakes(m, mail_error=ConnectionError("smtp fora do ar"))
    order = fakes.service().checkout("a@x", ITEMS)
    assert order["email_sent"] is False and len(fakes.saved) == 1 and all(c[0] != "refund" for c in fakes.calls)
    other = Fakes(m, mail_error=RuntimeError("bug no mailer"))
    with pytest.raises(RuntimeError, match="bug no mailer"):
        other.service().checkout("a@x", ITEMS)


def test_services_are_independent(load_exercise):
    m = load_exercise("ex01_constructor_injection")
    one, two = Fakes(m), Fakes(m)
    one.service().checkout("a@x", ITEMS)
    assert two.calls == [] and len(one.saved) == 1 and two.saved == []


# ---------- ex02 ----------
class Clock:
    pass


class Mailer:
    pass


class SmtpMailer(Mailer):
    pass


class FakeMailer(Mailer):
    pass


class Orders:
    pass


class Service:
    def __init__(self, orders: Orders, mailer: Mailer, clock: Clock, retries: int = 3):
        self.orders, self.mailer, self.clock, self.retries = orders, mailer, clock, retries


class Billing:
    def __init__(self, service: Service, orders: Orders):
        self.service, self.orders = service, orders


class A:
    def __init__(self, b: "B"):
        self.b = b


class B:
    def __init__(self, a: A):
        self.a = a


class NoHint:
    def __init__(self, x):
        self.x = x


class Defaulted:
    def __init__(self, n: int = 5, clock: Clock = None):
        self.n, self.clock = n, clock


def wired(m):
    c = m.Container()
    c.register(Clock)
    c.register(Orders)
    c.register(Mailer, SmtpMailer)
    c.register(Service)
    c.register(Billing, lifetime="transient")
    return c


def test_auto_wiring_and_lifetimes(load_exercise):
    m = load_exercise("ex02_container")
    c = wired(m)
    billing = c.resolve(Billing)
    assert isinstance(billing.service.mailer, SmtpMailer) and billing.service.retries == 3
    assert billing.orders is billing.service.orders and c.resolve(Service) is billing.service and c.resolve(Orders) is billing.orders
    assert c.resolve(Billing) is not billing and c.resolve(Billing).service is billing.service


def test_defaults_and_container_wins(load_exercise):
    m = load_exercise("ex02_container")
    c = m.Container()
    c.register(Defaulted)
    d = c.resolve(Defaulted)
    assert d.n == 5 and d.clock is None
    c.register(Clock)
    c.register(Defaulted)
    d2 = c.resolve(Defaulted)
    assert isinstance(d2.clock, Clock) and d2.n == 5


def test_instances_and_function_factories(load_exercise):
    m = load_exercise("ex02_container")
    c = m.Container()
    mailer = SmtpMailer()
    assert c.register_instance(Mailer, mailer) is mailer and c.resolve(Mailer) is mailer and c.has(Mailer) and not c.has(Orders)
    c.register(Clock)
    c.register(Orders)

    def make_service(orders: Orders, clock: Clock) -> Service:
        return Service(orders, FakeMailer(), clock, retries=9)

    c.register(Service, make_service)
    service = c.resolve(Service)
    assert isinstance(service.mailer, FakeMailer) and service.retries == 9 and service.orders is c.resolve(Orders)
    c.register(Orders, lambda: Orders(), lifetime="transient")
    assert c.resolve(Orders) is not c.resolve(Orders)


def test_resolution_errors(load_exercise):
    m = load_exercise("ex02_container")
    c = m.Container()
    with pytest.raises(LookupError) as top:
        c.resolve(Orders)
    assert str(top.value) == "não registrado: Orders"
    c.register(Service)
    with pytest.raises(LookupError) as nested:
        c.resolve(Service)
    assert str(nested.value) == "não registrado: Orders (cadeia: Service -> Orders)"
    c.register(Billing)
    with pytest.raises(LookupError) as deep:
        c.resolve(Billing)
    assert str(deep.value) == "não registrado: Orders (cadeia: Billing -> Service -> Orders)"
    c.register(NoHint)
    with pytest.raises(TypeError, match="parâmetro sem tipo: NoHint.x"):
        c.resolve(NoHint)
    with pytest.raises(ValueError, match="lifetime inválido: forever"):
        c.register(Clock, lifetime="forever")


def test_circular_dependency(load_exercise):
    m = load_exercise("ex02_container")
    c = m.Container()
    c.register(A)
    c.register(B)
    with pytest.raises(RuntimeError, match="dependência circular: A -> B -> A"):
        c.resolve(A)
    with pytest.raises(RuntimeError, match="dependência circular: B -> A -> B"):
        c.resolve(B)


def test_reregistering_and_failing_factories(load_exercise):
    m = load_exercise("ex02_container")
    c = m.Container()
    c.register(Clock)
    first = c.resolve(Clock)
    c.register(Clock)
    assert c.resolve(Clock) is not first                                        # registrar de novo esquece o singleton
    attempts = []

    def flaky() -> Orders:
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("primeira vez falha")
        return Orders()

    c.register(Orders, flaky)
    with pytest.raises(RuntimeError, match="primeira vez"):
        c.resolve(Orders)
    ok = c.resolve(Orders)
    assert isinstance(ok, Orders) and c.resolve(Orders) is ok and len(attempts) == 2


def test_override_rebuilds_singletons_and_cleans_up(load_exercise):
    m = load_exercise("ex02_container")
    c = wired(m)
    real = c.resolve(Service)
    assert isinstance(real.mailer, SmtpMailer)
    fake = FakeMailer()
    with c.override(Mailer, fake) as inside:
        assert inside is fake and c.resolve(Mailer) is fake
        service = c.resolve(Service)
        assert service is not real and service.mailer is fake and c.resolve(Billing).service.mailer is fake
    after = c.resolve(Service)
    assert isinstance(after.mailer, SmtpMailer) and after is not service
    with pytest.raises(RuntimeError, match="boom"):
        with c.override(Clock, "relógio de mentira"):
            raise RuntimeError("boom")
    assert isinstance(c.resolve(Clock), Clock)
    bare = m.Container()
    assert not bare.has(Mailer)
    with bare.override(Mailer, fake):
        assert bare.has(Mailer) and bare.resolve(Mailer) is fake
    assert not bare.has(Mailer)


def test_signatures_are_analysed_once(load_exercise, monkeypatch):
    m = load_exercise("ex02_container")
    calls, real = [], m.inspect.signature

    def counting(*a, **k):
        calls.append(1)
        return real(*a, **k)

    monkeypatch.setattr(m.inspect, "signature", counting)
    c = m.Container()
    for key in (Clock, Orders, Mailer):
        c.register(key, SmtpMailer if key is Mailer else None, lifetime="transient")
    c.register(Service, lifetime="transient")
    for _ in range(30):
        c.resolve(Service)
    assert len(calls) <= 4                                                      # 4 fábricas distintas, no máximo uma análise cada


# ---------- ex03 ----------
def test_wiring_by_environment(load_exercise):
    m = load_exercise("ex03_composition_root")
    dev = m.build_app(m.Settings())
    assert isinstance(dev.clock, m.SystemClock) and isinstance(dev.mailer, m.ConsoleMailer) and isinstance(dev.store, m.MemoryStore)
    test = m.build_app(m.Settings(env="test"))
    assert isinstance(test.clock, m.FixedClock) and test.clock() == datetime(2026, 1, 1, 12, 0) and isinstance(test.mailer, m.ConsoleMailer)
    prod = m.build_app(m.Settings(env="prod", store_path="/tmp/x.json"))
    assert isinstance(prod.clock, m.SystemClock) and isinstance(prod.mailer, m.SmtpMailer) and isinstance(prod.store, m.JsonFileStore) and prod.settings.env == "prod"
    for env in ("dev", "test"):
        assert isinstance(m.build_app(m.Settings(env=env, dry_run=True)).mailer, m.NullMailer)
    assert isinstance(m.build_app(m.Settings(env="prod", dry_run=True, store_path="x.json")).mailer, m.NullMailer)
    with_file = m.build_app(m.Settings(env="dev", store_path="dados.json"))
    assert isinstance(with_file.store, m.JsonFileStore) and str(with_file.store.path) == "dados.json"


def test_composition_errors(load_exercise):
    m = load_exercise("ex03_composition_root")
    with pytest.raises(ValueError, match="ambiente desconhecido: 'staging'"):
        m.build_app(m.Settings(env="staging"))
    with pytest.raises(ValueError, match="ambiente desconhecido: 'staging'"):
        m.build_app(m.Settings(env="staging", store_path="x.json"))
    with pytest.raises(ValueError, match="prod exige store_path"):
        m.build_app(m.Settings(env="prod"))
    with pytest.raises(TypeError, match="override desconhecido: logger"):
        m.build_app(m.Settings(), logger=object())
    with pytest.raises(TypeError, match="override desconhecido: logger"):
        m.build_app(m.Settings(env="staging"), logger=object())                 # os overrides são conferidos ANTES de tudo


def test_overrides_replace_components(load_exercise):
    m = load_exercise("ex03_composition_root")

    class FalsyMailer:
        def __len__(self):
            return 0

        def send(self, to, subject):
            pass

    mailer, store, clock = FalsyMailer(), m.MemoryStore(), m.FixedClock(datetime(2030, 5, 5))
    app = m.build_app(m.Settings(env="prod", store_path="x.json"), mailer=mailer, store=store, clock=clock)
    assert not mailer and app.mailer is mailer and app.store is store and app.clock is clock
    assert app.report.mailer is mailer and app.report.store is store and app.report.clock is clock
    assert app.report.run("vendas")["at"] == "2030-05-05T00:00:00" and store.records[0]["name"] == "vendas"
    partial = m.build_app(m.Settings(env="test"), mailer=m.NullMailer())
    assert isinstance(partial.mailer, m.NullMailer) and isinstance(partial.clock, m.FixedClock)


def test_report_runs_with_the_final_components(load_exercise):
    m = load_exercise("ex03_composition_root")
    app = m.build_app(m.Settings(env="test"))
    record = app.report.run("vendas")
    assert record == {"name": "vendas", "at": "2026-01-01T12:00:00"} and app.store.records == [record]
    assert app.mailer.lines == ["para equipe@x.com: relatório vendas"]
    assert app.report.store is app.store and app.report.mailer is app.mailer and app.report.clock is app.clock


def test_no_hidden_shared_state(load_exercise, tmp_path):
    m = load_exercise("ex03_composition_root")
    one, two = m.build_app(m.Settings(env="test")), m.build_app(m.Settings(env="test"))
    assert one.store is not two.store and one.mailer is not two.mailer and one.report is not two.report
    one.report.run("a")
    assert two.store.records == [] and two.mailer.lines == []
    path = tmp_path / "relatorios.json"
    app = m.build_app(m.Settings(env="dev", store_path=str(path)))
    app.report.run("a")
    app.report.run("b")
    assert [r["name"] for r in json.loads(path.read_text(encoding="utf-8"))] == ["a", "b"]


# ---------- ex04 ----------
def test_scope_basics(load_exercise):
    m = load_exercise("ex04_scoped_context")
    assert m.in_request() is False and m.log_prefix() == "[-] "
    for call in (m.current_request_id, m.current_user):
        with pytest.raises(LookupError, match="fora de uma requisição"):
            call()
    with m.request_scope("req-1", "ana"):
        assert m.in_request() is True and m.current_request_id() == "req-1" and m.current_user() == "ana" and m.log_prefix() == "[req-1 ana] "
    with m.request_scope("req-2"):
        assert m.current_user() is None and m.log_prefix() == "[req-2 anônimo] "
    assert m.in_request() is False and m.log_prefix() == "[-] "


def test_nested_scopes_and_exceptions_restore(load_exercise):
    m = load_exercise("ex04_scoped_context")
    with m.request_scope("outer", "ana"):
        with m.request_scope("inner", "bia"):
            assert m.log_prefix() == "[inner bia] "
        assert m.log_prefix() == "[outer ana] "
        with pytest.raises(RuntimeError, match="boom"):
            with m.request_scope("failing"):
                assert m.current_request_id() == "failing"
                raise RuntimeError("boom")
        assert m.log_prefix() == "[outer ana] "
    assert not m.in_request()
    for bad in ("", "   ", None, 7):
        with pytest.raises(ValueError, match="request_id inválido"):
            with m.request_scope(bad, "ana"):
                pass
    assert not m.in_request()


def test_threads_do_not_inherit_the_context_by_themselves(load_exercise):
    m = load_exercise("ex04_scoped_context")
    seen = []
    with m.request_scope("req-9", "ana"):
        plain = threading.Thread(target=lambda: seen.append(m.in_request()))
        plain.start()
        plain.join()
        assert seen == [False]                                                   # uma thread nova começa com o contexto VAZIO
        assert m.run_in_thread(m.current_request_id) == "req-9"
        assert m.run_in_thread(m.log_prefix) == "[req-9 ana] "
        assert m.run_in_thread(lambda a, b: a + b, 2, 3) == 5


def test_run_in_thread_errors_and_isolation(load_exercise):
    m = load_exercise("ex04_scoped_context")
    with pytest.raises(LookupError, match="fora de uma requisição"):
        m.run_in_thread(m.current_request_id)                                    # sem escopo, o erro da função sobe
    with m.request_scope("req-1", "ana"):
        def inner():
            with m.request_scope("dentro-da-thread", "zé"):
                return m.log_prefix()

        assert m.run_in_thread(inner) == "[dentro-da-thread zé] "
        assert m.current_request_id() == "req-1"                                 # o que a thread mudou não vaza para quem chamou

        def boom():
            raise KeyError("falhou na thread")

        with pytest.raises(KeyError, match="falhou na thread"):
            m.run_in_thread(boom)


def test_asyncio_tasks_each_see_their_own_scope(load_exercise):
    m = load_exercise("ex04_scoped_context")

    async def worker(request_id, delay):
        with m.request_scope(request_id, user=f"u-{request_id}"):
            await asyncio.sleep(delay)
            return m.log_prefix()

    async def main():
        return await asyncio.gather(worker("a", 0.03), worker("b", 0.01), worker("c", 0.02))

    assert asyncio.run(main()) == ["[a u-a] ", "[b u-b] ", "[c u-c] "]
    assert not m.in_request()


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["di_classico", "di_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
