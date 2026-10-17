import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_mailer_adapter(load_exercise):
    m = load_exercise("ex01_object_adapter")
    mailer = m.OldMailer()
    adapter = m.MailerAdapter(mailer, {"ana": "ana@x.com", "vazio": ""})
    assert adapter.notify("ana", "Seu pedido foi enviado e chegará em breve, aguarde!", "high") is True
    assert mailer.sent == [("ana@x.com", "[HIGH] "+"Seu pedido foi enviado e chega", "Seu pedido foi enviado e chegará em breve, aguarde!", 5)]
    assert adapter.notify("ana", "oi") is True and mailer.sent[-1][3] == 3
    assert adapter.notify("ana", "oi", "low") is True and mailer.sent[-1][3] == 1
    assert adapter.notify("vazio", "oi") is False
    with pytest.raises(LookupError, match="usuário sem e-mail: bia"):
        adapter.notify("bia", "oi")
    with pytest.raises(ValueError, match="nível inválido: urgent"):
        adapter.notify("ana", "oi", "urgent")


def test_sms_adapter(load_exercise):
    m = load_exercise("ex01_object_adapter")
    gw = m.SmsGateway()
    adapter = m.SmsAdapter(gw, {"ana": "+5511999", "sem": ""})
    assert adapter.notify("ana", "oi", "low") is True and gw.pushed == [("+5511999", "LOW: oi")]
    assert adapter.notify("sem", "oi") is False
    long = "x" * 300
    assert adapter.notify("ana", long) is True
    sent = gw.pushed[-1][1]
    assert len(sent) == 160 and sent.endswith("…") and sent.startswith("NORMAL: xxx")
    exactly = "y" * (160 - len("NORMAL: "))
    adapter.notify("ana", exactly)
    assert len(gw.pushed[-1][1]) == 160 and not gw.pushed[-1][1].endswith("…")
    with pytest.raises(LookupError, match="usuário sem telefone: zé"):
        adapter.notify("zé", "oi")
    with pytest.raises(ValueError, match="nível inválido"):
        adapter.notify("ana", "oi", "x")


def test_notify_all_and_duck_typing(load_exercise):
    m = load_exercise("ex01_object_adapter")
    mail, sms = m.OldMailer(), m.SmsGateway()
    notifiers = [m.MailerAdapter(mail, {"ana": "ana@x.com"}), m.SmsAdapter(sms, {"bia": "+55"})]
    assert m.notify_all(notifiers, "ana", "oi") == [True, False]
    assert m.notify_all(notifiers, "bia", "oi") == [False, True]
    assert m.notify_all(notifiers, "zé", "oi") == [False, False]

    class Fake:                                                          # qualquer objeto com notify serve: não precisa herdar
        def notify(self, user, message, level="normal"):
            return True

    class Boom:
        def notify(self, user, message, level="normal"):
            raise RuntimeError("falha")

    assert m.notify_all([Fake(), Fake()], "x", "y") == [True, True]
    with pytest.raises(RuntimeError):
        m.notify_all([Fake(), Boom()], "x", "y")
    assert m.notify_all([], "x", "y") == []


# ---------- ex02 ----------
def legacy_area(w, h, unit="m"):
    """Área."""
    return f"{w * h}{unit}2"


def test_adapt_rename_defaults_result(load_exercise):
    m = load_exercise("ex02_function_adapter")
    area = m.adapt(legacy_area, rename={"width": "w", "height": "h"}, convert_result=lambda s: s.upper())
    assert area(width=2, height=3) == "6M2"
    assert area(2, height=3) == "6M2" and area(2, 3, unit="cm") == "6CM2"
    assert area.__name__ == "legacy_area" and area.__doc__ == "Área." and area.__wrapped__ is legacy_area
    sized = m.adapt(legacy_area, rename={"width": "w"}, defaults={"h": 10, "unit": "km"})
    assert sized(width=2) == "20km2"
    assert sized(2, 5) == "10km2"                                          # h posicional: o padrão NÃO substitui
    assert sized(2, unit="m") == "20m2"


def test_adapt_convert_args_and_errors(load_exercise):
    m = load_exercise("ex02_function_adapter")
    area = m.adapt(legacy_area, rename={"width": "w"}, convert_args={"w": float, "h": int})
    assert area(width="2.5", h="4") == "10.0m2"
    assert area("3", 2) == "6.0m2"
    with pytest.raises(TypeError, match="argumento repetido: w"):
        area(width=1, w=2, h=3)
    for kwargs, name in [({"rename": {"x": "zzz"}}, "zzz"), ({"defaults": {"nope": 1}}, "nope"), ({"convert_args": {"q": int}}, "q")]:
        with pytest.raises(ValueError, match=f"parâmetro inexistente: {name}"):
            m.adapt(legacy_area, **kwargs)
    plain = m.adapt(legacy_area)
    assert plain(2, 3) == "6m2"


# ---------- ex03 ----------
class OldCounter:
    def __init__(self):
        self.n = 0
        self.label = "c"

    def incr(self):
        self.n += 1
        return self.n


def test_renamed_read_write_delete(load_exercise):
    m = load_exercise("ex03_attr_adapter")
    c = OldCounter()
    r = m.Renamed(c, {"increment": "incr", "value": "n"})
    assert r.increment() == 1 and r.value == 1 and c.n == 1
    r.value = 10
    assert c.n == 10 and r.increment() == 11
    assert r.label == "c"                                                  # fora do mapeamento: passa direto
    r.label = "novo"
    assert c.label == "novo"
    del r.label
    assert not hasattr(c, "label")
    with pytest.raises(AttributeError):
        r.label
    with pytest.raises(AttributeError):
        r.zzz
    assert r.unwrap() is c


def test_renamed_dir_repr_validation(load_exercise):
    m = load_exercise("ex03_attr_adapter")
    c = OldCounter()
    r = m.Renamed(c, {"increment": "incr", "value": "n"})
    names = dir(r)
    assert "increment" in names and "value" in names and "incr" not in names and "n" not in names and "label" in names
    assert names == sorted(names) and len(names) == len(set(names))
    assert repr(r).startswith("Renamed(<") and "OldCounter" in repr(r)
    with pytest.raises(ValueError, match="atributo inexistente: nada"):
        m.Renamed(c, {"x": "nada"})
    assert m.Renamed(c, {}).incr() == 1


# ---------- ex04 ----------
@pytest.mark.parametrize("value,cents", [("12,50", 1250), ("1.234,5", 123450), ("12.5", 1250), (12.5, 1250), (3, 300), ("0,005", 1), ("0,004", 0), (0.1 + 0.2, 30), ("  7 ", 700), (1.005, 101)])
def test_parse_price(load_exercise, value, cents):
    m = load_exercise("ex04_data_adapter")
    assert m.parse_price(value) == cents


@pytest.mark.parametrize("bad", ["abc", None, True, "", [1], "1,2,3", "nan"])
def test_parse_price_invalid(load_exercise, bad):
    m = load_exercise("ex04_data_adapter")
    with pytest.raises(ValueError, match="preço inválido"):
        m.parse_price(bad)


def test_parse_price_negative_and_bool(load_exercise):
    m = load_exercise("ex04_data_adapter")
    with pytest.raises(ValueError, match="preço negativo"):
        m.parse_price("-1,00")
    with pytest.raises(ValueError, match="preço negativo"):
        m.parse_price(-3)
    for yes in (True, " SIM ", "s", "1", "True", 1):
        assert m.parse_bool(yes) is True
    for no in (False, "N", "nao", "NÃO", "0", "false", 0):
        assert m.parse_bool(no) is False
    for bad in ("talvez", None, 2, ""):
        with pytest.raises(ValueError, match="booleano inválido"):
            m.parse_bool(bad)


def test_adapt_product(load_exercise):
    m = load_exercise("ex04_data_adapter")
    raw = {"codigo": " ab-12 ", "nome": "  Lápis  ", "preco": "1.234,50", "etiquetas": "Escola; papelaria;;ESCOLA ; ", "estoque": "S", "extra": "ignorado"}
    p = m.adapt_product(raw)
    assert p == m.Product("AB-12", "Lápis", 123450, ("escola", "papelaria"), True)
    assert m.adapt_product({"codigo": "x", "nome": "n", "preco": 1, "estoque": "N"}).tags == ()
    assert m.adapt_product({"codigo": "x", "nome": "n", "preco": 1, "estoque": "N", "etiquetas": None}).tags == ()


def test_adapt_product_errors_order(load_exercise):
    m = load_exercise("ex04_data_adapter")
    with pytest.raises(ValueError, match="campo ausente: codigo"):
        m.adapt_product({})
    with pytest.raises(ValueError, match="campo ausente: preco"):
        m.adapt_product({"codigo": "x", "nome": "n", "estoque": "S"})
    with pytest.raises(ValueError, match="campo ausente: estoque"):
        m.adapt_product({"codigo": "x", "nome": "n", "preco": 1})
    with pytest.raises(ValueError, match="nome vazio"):
        m.adapt_product({"codigo": "x", "nome": "  ", "preco": 1, "estoque": "S"})


def test_adapt_many_collects_errors(load_exercise):
    m = load_exercise("ex04_data_adapter")
    rows = [
        {"codigo": "a", "nome": "A", "preco": "1,00", "estoque": "S"},
        {"codigo": "b", "nome": "B", "preco": "abc", "estoque": "S"},
        {"codigo": "c", "nome": "C", "preco": "2,00", "estoque": "talvez"},
        {"codigo": "d", "nome": "D", "preco": "3,00", "estoque": "N"},
    ]
    products, errors = m.adapt_many(rows)
    assert [p.sku for p in products] == ["A", "D"]
    assert errors == [(1, "preço inválido: 'abc'"), (2, "booleano inválido: 'talvez'")]
    assert m.adapt_many([]) == ([], [])


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["adapter_classico", "adapter_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
