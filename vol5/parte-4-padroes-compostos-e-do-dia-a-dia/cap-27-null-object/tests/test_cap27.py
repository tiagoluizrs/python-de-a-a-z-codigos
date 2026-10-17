import copy
import logging
import subprocess
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_real_customer(load_exercise):
    m = load_exercise("ex01_null_customer")
    c = m.RealCustomer("  Ana ", 10)
    assert c.name == "Ana" and c.discount_pct == 10 and c.points == 0 and c.is_null is False
    assert c.greeting() == "Olá, Ana!" and c.price(1000) == 900 and c.price(999) == 899 and c.price(0) == 0
    c.add_points(5)
    c.add_points(2)
    assert c.points == 7 and m.RealCustomer("Bia").discount_pct == 0
    for call, message in (
        (lambda: m.RealCustomer("  "), "nome vazio"),
        (lambda: m.RealCustomer("a", 101), "desconto inválido"),
        (lambda: m.RealCustomer("a", -1), "desconto inválido"),
        (lambda: m.RealCustomer("a", True), "desconto inválido"),
        (lambda: m.RealCustomer("a", 5.5), "desconto inválido"),
        (lambda: c.add_points(0), "pontos inválidos"),
        (lambda: c.add_points(True), "pontos inválidos"),
        (lambda: c.price(-1), "valor inválido"),
        (lambda: c.price(1.5), "valor inválido"),
    ):
        with pytest.raises(ValueError, match=message):
            call()


def test_null_customer(load_exercise):
    m = load_exercise("ex01_null_customer")
    n = m.NullCustomer()
    assert n is m.NullCustomer() and isinstance(n, m.Customer)
    assert n.is_null is True and n.name == "visitante" and n.discount_pct == 0 and n.points == 0 and bool(n) is False and repr(n) == "NullCustomer()"
    assert n.greeting() == "Olá, visitante! Cadastre-se para ganhar descontos."
    assert n.price(1000) == 1000
    n.add_points(50)
    n.add_points(-3)                                           # a ausência ignora tudo
    assert n.points == 0
    for name in ("name", "points", "novo"):
        with pytest.raises(AttributeError):
            setattr(n, name, 1)
    with pytest.raises(ValueError, match="valor inválido"):
        n.price(-1)
    with pytest.raises(TypeError):
        m.Customer()


def test_repository(load_exercise):
    m = load_exercise("ex01_null_customer")
    repo = m.CustomerRepository()
    ana, bia = m.RealCustomer("Ana", 10), m.RealCustomer("Bia")
    repo.add(2, bia)
    repo.add(1, ana)
    assert repo.find(1) is ana and repo.find(99) is m.NullCustomer() and repo.find(99) is not None
    assert repo.find_strict(2) is bia and repo.names() == ["Ana", "Bia"] and len(repo) == 2
    with pytest.raises(KeyError, match="cliente inexistente: 99"):
        repo.find_strict(99)
    with pytest.raises(ValueError, match="id repetido: 1"):
        repo.add(1, m.RealCustomer("Clara"))
    with pytest.raises(ValueError, match="cliente nulo não pode ser cadastrado"):
        repo.add(3, m.NullCustomer())
    with pytest.raises(TypeError):
        repo.add(3, "Clara")
    assert len(repo) == 2


LINES = [("café", 2, 350), ("pão", 1, 120)]


def test_order_with_real_and_null_customers(load_exercise):
    m = load_exercise("ex01_null_customer")
    ana = m.RealCustomer("Ana", 10)
    order = m.Order(ana, LINES)
    assert order.subtotal() == 820 and order.total() == 738
    assert order.earn_points() == 7 and ana.points == 7
    assert order.summary() == "Olá, Ana! Total: R$ 7,38"
    guest = m.Order(m.NullCustomer(), LINES)
    assert guest.subtotal() == 820 and guest.total() == 820 and guest.earn_points() == 8 and m.NullCustomer().points == 0
    assert guest.summary() == "Olá, visitante! Cadastre-se para ganhar descontos. Total: R$ 8,20"
    small = m.Order(ana, [("bala", 1, 50)])
    assert small.earn_points() == 0 and ana.points == 7                  # nada de add_points(0), que seria um erro


def test_order_validation(load_exercise):
    m = load_exercise("ex01_null_customer")
    ana = m.RealCustomer("Ana")
    for line in (("x", 0, 10), ("x", -1, 10), ("x", True, 10), ("x", 1.5, 10)):
        with pytest.raises(ValueError, match="quantidade inválida"):
            m.Order(ana, [line])
    for line in (("x", 1, -1), ("x", 1, 2.5)):
        with pytest.raises(ValueError, match="valor inválido"):
            m.Order(ana, [line])
    assert m.Order(ana, []).subtotal() == 0


def test_order_never_asks_is_null(load_exercise):
    m = load_exercise("ex01_null_customer")

    class Spy(m.Customer):
        def __init__(self):
            self.null_checks, self.added = 0, []

        @property
        def is_null(self):
            self.null_checks += 1
            return False

        name = property(lambda self: "spy")
        discount_pct = property(lambda self: 0)
        points = property(lambda self: 0)

        def greeting(self):
            return "oi"

        def price(self, cents):
            return cents

        def add_points(self, points):
            self.added.append(points)

    spy = Spy()
    order = m.Order(spy, LINES)
    order.total()
    order.earn_points()
    order.summary()
    assert spy.null_checks == 0 and spy.added == [8]


# ---------- ex02 ----------
class Recording:
    def __init__(self):
        self.infos, self.errors = [], []

    def info(self, message):
        self.infos.append(message)

    def error(self, message):
        self.errors.append(message)


class FalsyLogger(Recording):
    def __len__(self):
        return len(self.infos)


class DictCache:
    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def __len__(self):
        return len(self.data)


class FakeNotifier:
    def __init__(self, result=True):
        self.sent, self.result = [], result

    def send(self, to, message):
        self.sent.append((to, message))
        return self.result


def test_null_collaborators_do_nothing(load_exercise):
    m = load_exercise("ex02_null_collaborators")
    for name in ("info", "warning", "error"):
        assert getattr(m.NullLogger(), name)("msg", 1, 2, a=3) is None
    cache = m.NullCache()
    assert cache.get("k") is None and cache.get("k", 5) == 5 and cache.set("k", 1) is None
    assert cache.get("k", 5) == 5 and "k" not in cache and len(cache) == 0
    assert m.NullNotifier().send("a@b", "oi") is False


def test_service_defaults_to_null_objects(load_exercise):
    m = load_exercise("ex02_null_collaborators")
    calls = []
    service = m.ReportService(lambda key: calls.append(key) or len(key))
    assert service.logger is m.NULL_LOGGER and service.cache is m.NULL_CACHE and service.notifier is m.NULL_NOTIFIER
    assert service.report("abc") == 3 and service.report("abc") == 3 and calls == ["abc", "abc"]      # o NullCache nunca guarda
    assert service.report_and_notify("abcd", "x@y") == (4, False)


def test_service_with_real_collaborators(load_exercise):
    m = load_exercise("ex02_null_collaborators")
    log, cache, notifier, calls = Recording(), DictCache(), FakeNotifier(), []
    service = m.ReportService(lambda key: calls.append(key) or key.upper(), log, cache, notifier)
    assert service.logger is log and service.cache is cache and service.notifier is notifier
    assert service.report("k") == "K" and service.report("k") == "K" and calls == ["k"]
    assert log.infos == ["calculado: k", "cache hit: k"] and cache.data == {"k": "K"}
    assert service.report_and_notify("k", "ana@x") == ("K", True)
    assert notifier.sent == [("ana@x", "relatório k: K")] and log.errors == []


def test_falsy_collaborators_are_still_used(load_exercise):
    m = load_exercise("ex02_null_collaborators")
    log, cache = FalsyLogger(), DictCache()
    assert not log and not cache                                          # vazios, logo FALSOS
    service = m.ReportService(lambda key: 1, log, cache)
    assert service.logger is log and service.cache is cache
    service.report("a")
    assert cache.data == {"a": 1} and log.infos == ["calculado: a"]


def test_service_failures(load_exercise):
    m = load_exercise("ex02_null_collaborators")
    log, cache = Recording(), DictCache()

    def boom(key):
        raise ValueError("ruim")

    service = m.ReportService(boom, log, cache)
    with pytest.raises(ValueError, match="ruim"):
        service.report("k")
    assert log.errors == ["falhou: k: ValueError"] and cache.data == {} and log.infos == []
    ok = m.ReportService(lambda key: 7, log, DictCache(), FakeNotifier(result=False))
    assert ok.report_and_notify("k", "x@y") == (7, False)
    assert log.errors[-1] == "não enviado para x@y"
    quiet = m.ReportService(boom)
    with pytest.raises(ValueError):
        quiet.report("k")                                                 # com o NullLogger o erro também sobe


# ---------- ex03 ----------
def test_null_singleton_and_absorption(load_exercise):
    m = load_exercise("ex03_chameleon_null")
    assert m.NULL is m.Null() and m.Null() is m.Null()
    n = m.NULL
    assert n.a.b.c is n and n(1, x=2) is n and n["k"] is n and n.method().other is n
    with pytest.raises(AttributeError):
        n.__foo__
    assert not hasattr(n, "__foo__") and getattr(n, "__foo__", "padrão") == "padrão"


def test_null_behaves_as_empty_and_falsy(load_exercise):
    m = load_exercise("ex03_chameleon_null")
    n = m.NULL
    assert bool(n) is False and len(n) == 0 and list(n) == [] and (1 in n) is False and str(n) == "" and repr(n) == "Null"
    assert (n or "padrão") == "padrão"
    assert [x for x in n] == []


def test_null_equality_and_hash(load_exercise):
    m = load_exercise("ex03_chameleon_null")
    n = m.NULL
    assert n == n and n == None and None == n and n != 0 and n != "" and n != False and (n == 0) is False  # noqa: E711
    assert hash(n) == hash(None) and {n: 1}[None] == 1


def test_null_arithmetic(load_exercise):
    m = load_exercise("ex03_chameleon_null")
    n = m.NULL
    assert n + 1 is n and 1 + n is n and n - 1 is n and 1 - n is n and n * 2 is n and 2 * n is n and n / 3 is n and 3 / n is n


def test_null_is_immutable_and_a_context_manager(load_exercise):
    m = load_exercise("ex03_chameleon_null")
    n = m.NULL
    with pytest.raises(AttributeError, match="Null é imutável"):
        n.x = 1
    with pytest.raises(AttributeError, match="Null é imutável"):
        setattr(n, "name", 1)
    with pytest.raises(AttributeError, match="Null é imutável"):
        del n.x
    with n as inside:
        assert inside is n
    with pytest.raises(ValueError):
        with n:
            raise ValueError("a exceção não pode ser engolida")


def test_null_copy_and_is_null(load_exercise):
    m = load_exercise("ex03_chameleon_null")
    assert copy.copy(m.NULL) is m.NULL and copy.deepcopy(m.NULL) is m.NULL and copy.deepcopy({"a": [m.NULL]})["a"][0] is m.NULL
    assert m.is_null(m.NULL) is True and m.is_null(None) is False and m.is_null(0) is False and m.is_null("") is False


def test_dig(load_exercise):
    m = load_exercise("ex03_chameleon_null")
    data = {"a": {"b": {"c": 1}}, "zero": {"v": 0}, "empty": {"v": ""}, "no": {"v": False}, "nothing": {"v": None}, "items": [1, 2]}
    assert m.dig(data, "a.b.c") == 1 and m.dig(data, "a.b") == {"c": 1} and m.dig(data, "a.x.c") is None and m.dig(data, "a.x.c", "padrão") == "padrão"
    for path, value in (("zero.v", 0), ("empty.v", ""), ("no.v", False), ("nothing.v", None)):
        assert m.dig(data, path, "padrão") == value and m.dig(data, path, "padrão") is value
    assert m.dig(data, "") is data
    assert m.dig(data, "items.0", "d") == "d" and m.dig({"a": 1}, "a.b", "d") == "d" and m.dig(None, "a", "d") == "d"
    obj = SimpleNamespace(db=SimpleNamespace(host="h", port=0), tags={"x": 1})
    assert m.dig(obj, "db.host") == "h" and m.dig(obj, "db.port", 5432) == 0 and m.dig(obj, "tags.x") == 1 and m.dig(obj, "db.user", "root") == "root"


# ---------- ex04 ----------
def test_names_of_and_first_or(load_exercise):
    m = load_exercise("ex04_safe_defaults")
    assert m.names_of(None) == [] and m.names_of([]) == [] and m.names_of([{"name": "Ana"}, {"name": "Bia"}]) == ["Ana", "Bia"]
    assert m.first_or([3, 4]) == 3 and m.first_or([]) is None and m.first_or([], "d") == "d" and m.first_or(None, "d") == "d" and m.first_or([0]) == 0
    consumed = []

    def gen():
        for i in range(5):
            consumed.append(i)
            yield i

    assert m.first_or(gen()) == 0 and consumed == [0]
    assert m.first_or(iter(()), "vazio") == "vazio" and m.first_or("abc") == "a"


def test_setting(load_exercise):
    m = load_exercise("ex04_safe_defaults")
    config = {"db": {"port": 0, "host": "", "debug": False, "pass": None}, "name": "app", "items": [1]}
    assert m.setting(config, "name") == "app" and m.setting(config, "db.port", 5432) == 0 and m.setting(config, "db.host", "x") == ""
    assert m.setting(config, "db.debug", True) is False and m.setting(config, "db.pass", "x") is None
    assert m.setting(config, "db.user", "root") == "root" and m.setting(config, "x.y.z", 9) == 9 and m.setting(config, "x") is None
    assert m.setting(config, "name.first", "d") == "d" and m.setting(config, "items.0", "d") == "d" and m.setting(None, "a", "d") == "d"
    assert m.setting(config, "db") == config["db"]


def test_locked(load_exercise):
    m = load_exercise("ex04_safe_defaults")
    lock = threading.Lock()
    assert m.locked(lock) is lock
    with m.locked(lock):
        assert lock.locked()
    assert not lock.locked()
    with m.locked(None) as value:
        assert value is None
    with m.locked():
        pass

    class FalsyLock:
        entered = 0

        def __len__(self):
            return 0

        def __enter__(self):
            FalsyLock.entered += 1

        def __exit__(self, *exc):
            return False

    falsy = FalsyLock()
    assert not falsy and m.locked(falsy) is falsy
    with m.locked(falsy):
        pass
    assert FalsyLock.entered == 1


def test_quiet_logger(load_exercise, caplog):
    m = load_exercise("ex04_safe_defaults")
    logging.getLogger("cap27.quiet").addHandler(logging.StreamHandler())
    logger = m.quiet_logger("cap27.quiet")
    assert logger is logging.getLogger("cap27.quiet") and logger.propagate is False
    assert len(logger.handlers) == 1 and isinstance(logger.handlers[0], logging.NullHandler)
    assert m.quiet_logger("cap27.quiet") is logger and len(logger.handlers) == 1
    with caplog.at_level(logging.DEBUG):
        logger.warning("não deve aparecer")
        logger.error("nem este")
    assert caplog.records == []
    other = m.quiet_logger("cap27.other")
    assert other is not logger and len(other.handlers) == 1


def test_run_tasks(load_exercise):
    m = load_exercise("ex04_safe_defaults")
    assert m.run_tasks([lambda: 1, lambda: 2, lambda: 3]) == [1, 2, 3] and m.run_tasks([]) == []
    seen = []
    assert m.run_tasks((lambda i=i: i * 10 for i in range(3)), lambda i, total, result: seen.append((i, total, result))) == [0, 10, 20]
    assert seen == [(1, 3, 0), (2, 3, 10), (3, 3, 20)]
    ran, seen = [], []

    def boom():
        raise RuntimeError("falhou")

    with pytest.raises(RuntimeError):
        m.run_tasks([lambda: ran.append("a") or "a", boom, lambda: ran.append("c")], lambda *a: seen.append(a))
    assert ran == ["a"] and seen == [(1, 3, "a")]


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["null_classico", "null_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
