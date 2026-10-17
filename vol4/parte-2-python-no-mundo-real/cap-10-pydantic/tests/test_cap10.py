import json
from decimal import Decimal

import pytest
from pydantic import ValidationError


# ---------- ex01 ----------
def test_user_normalizes(load_exercise):
    m = load_exercise("ex01_user_model")
    user = m.User(name="  Ana   Maria  Souza ", email=" ANA@Exemplo.COM ", age="30", tags=["Python", "python", "SQL", "PYTHON", "sql"],
                  address={"street": " Rua A ", "city": "Recife", "zip_code": "12345-678"})
    assert user.name == "Ana Maria Souza" and user.email == "ana@exemplo.com" and user.age == 30
    assert user.tags == ["python", "sql"] and user.address.zip_code == "12345678" and user.address.street == "Rua A"
    assert m.User(name="x", email="a@b.co", age=0).tags == [] and m.User(name="x", email="a@b.co", age=0).address is None


def test_user_rejects_bad_data(load_exercise):
    m = load_exercise("ex01_user_model")
    base = {"name": "Ana", "email": "a@b.co", "age": 20}
    for patch in ({"name": "   "}, {"email": "sem-arroba"}, {"email": "a@b"}, {"age": -1}, {"age": 151}, {"age": "vinte"},
                  {"extra": 1}, {"address": {"street": "x", "city": "y", "zip_code": "123"}}, {"address": {"street": " ", "city": "y", "zip_code": "12345678"}},
                  {"address": {"street": "x", "city": "y", "zip_code": "12345678", "country": "BR"}}):
        with pytest.raises(ValidationError):
            m.User(**{**base, **patch})


def test_user_is_frozen(load_exercise):
    m = load_exercise("ex01_user_model")
    user = m.User(name="Ana", email="a@b.co", age=20)
    with pytest.raises(ValidationError):
        user.age = 21
    assert user.model_dump()["tags"] == []


# ---------- ex02 ----------
def make_error(load_exercise):
    m = load_exercise("ex01_user_model")
    with pytest.raises(ValidationError) as info:
        m.User(name="  ", email="sem-arroba", age=-1, tags=[1], address={"street": "x", "city": "y", "zip_code": "1"})
    return info.value


def test_errors_to_dict(load_exercise):
    report = load_exercise("ex02_error_report")
    result = report.errors_to_dict(make_error(load_exercise))
    assert set(result) == {"name", "email", "age", "tags.0", "address.zip_code"}
    assert result["name"] == ["nome em branco"] or result["name"] == ["Value error, nome em branco"] or "branco" in result["name"][0]
    assert all(not m.startswith("Value error, ") for messages in result.values() for m in messages)
    assert result["age"][0].startswith("Input should be greater than or equal to 0")


def test_errors_to_dict_root_and_lists(load_exercise):
    report = load_exercise("ex02_error_report")
    from pydantic import BaseModel, model_validator

    class Order(BaseModel):
        items: list[dict]

        @model_validator(mode="after")
        def non_empty(self):
            if not self.items:
                raise ValueError("pedido vazio")
            return self

    with pytest.raises(ValidationError) as info:
        Order(items=[])
    assert report.errors_to_dict(info.value) == {"__root__": ["pedido vazio"]}
    with pytest.raises(ValidationError) as info:
        Order(items="x")
    assert list(report.errors_to_dict(info.value)) == ["items"]


def test_first_message(load_exercise):
    report = load_exercise("ex02_error_report")
    error = make_error(load_exercise)
    text = report.first_message(error)
    assert text.startswith("name: ") and text.endswith(f"(+{error.error_count() - 1} erros)")
    from pydantic import BaseModel

    class Two(BaseModel):
        a: int
        b: int

    with pytest.raises(ValidationError) as info:
        Two(a="x", b=1)
    assert report.first_message(info.value).startswith("a: ") and "(+" not in report.first_message(info.value)
    with pytest.raises(ValidationError) as info:
        Two(a="x", b="y")
    assert report.first_message(info.value).endswith("(+1 erro)")


# ---------- ex03 ----------
def test_shapes_union(load_exercise):
    m = load_exercise("ex03_shapes")
    shapes = m.parse_shapes([{"kind": "circle", "radius": 2}, {"kind": "rect", "width": 3, "height": "4"}, {"kind": "square", "side": 5, "area": 999}])
    assert [type(s).__name__ for s in shapes] == ["Circle", "Rect", "Square"]
    assert [s.area for s in shapes] == [12.57, 12.0, 25.0]                                 # a "area" de entrada foi ignorada
    assert shapes[0].model_dump()["area"] == 12.57
    assert m.total_area([{"kind": "rect", "width": 2, "height": 3}, {"kind": "square", "side": 1}]) == 7.0 and m.total_area([]) == 0.0


def test_shapes_errors(load_exercise):
    m = load_exercise("ex03_shapes")
    with pytest.raises(ValidationError) as info:
        m.parse_shapes([{"kind": "triangulo"}])
    assert info.value.errors()[0]["type"] == "union_tag_invalid"
    with pytest.raises(ValidationError) as info:
        m.parse_shapes([{"kind": "rect", "width": 0, "height": 1}])
    assert [e["loc"] for e in info.value.errors()] == [(0, "rect", "width")]               # só os erros do modelo certo
    with pytest.raises(ValidationError):
        m.parse_shapes([{"radius": 1}])


# ---------- ex04 ----------
ENV = {"SHOP_SECRET_KEY": "super-secreta", "SHOP_DATABASE_URL": "postgresql://u:p@h/db"}


def set_env(monkeypatch, **extra):
    for key in list(__import__("os").environ):
        if key.startswith("SHOP_"):
            monkeypatch.delenv(key)
    for key, value in {**ENV, **extra}.items():
        monkeypatch.setenv(key, value)


def test_settings_defaults_and_secrets(load_exercise, monkeypatch):
    m = load_exercise("ex04_settings")
    set_env(monkeypatch)
    s = m.AppSettings()
    assert (s.environment, s.debug, s.port, s.allowed_hosts) == ("dev", False, 8000, ["localhost"])
    assert (s.redis.host, s.redis.port) == ("localhost", 6379)
    assert "super-secreta" not in repr(s) and s.secret_key.get_secret_value() == "super-secreta"


def test_settings_env_overrides(load_exercise, monkeypatch):
    m = load_exercise("ex04_settings")
    set_env(monkeypatch, SHOP_ENVIRONMENT="staging", SHOP_DEBUG="true", SHOP_PORT="9000", SHOP_ALLOWED_HOSTS='["a.test", "b.test"]',
            SHOP_REDIS__HOST="cache", SHOP_REDIS__PORT="6380", SHOP_UNKNOWN="ignorada")
    s = m.AppSettings()
    assert s.environment == "staging" and s.debug is True and s.port == 9000 and s.allowed_hosts == ["a.test", "b.test"]
    assert (s.redis.host, s.redis.port) == ("cache", 6380)


@pytest.mark.parametrize("extra, missing", [
    ({"SHOP_ENVIRONMENT": "prod", "SHOP_DEBUG": "1"}, "debug"),
    ({"SHOP_ENVIRONMENT": "prod", "SHOP_ALLOWED_HOSTS": '["*"]'}, "não é permitido"),
    ({"SHOP_PORT": "70000"}, "port"),
    ({"SHOP_SECRET_KEY": "curta"}, "8 caracteres"),
    ({"SHOP_DATABASE_URL": "sqlite:///x.db"}, "postgresql"),
    ({"SHOP_ENVIRONMENT": "producao"}, "environment"),
])
def test_settings_validation(load_exercise, monkeypatch, extra, missing):
    m = load_exercise("ex04_settings")
    set_env(monkeypatch, **extra)
    with pytest.raises(ValidationError) as info:
        m.AppSettings()
    assert missing in str(info.value)


def test_settings_required(load_exercise, monkeypatch):
    m = load_exercise("ex04_settings")
    set_env(monkeypatch)
    monkeypatch.delenv("SHOP_SECRET_KEY")
    with pytest.raises(ValidationError) as info:
        m.AppSettings()
    assert info.value.errors()[0]["type"] == "missing"


# ---------- ex05 ----------
def make_model():
    from pydantic import BaseModel, Field

    class Row(BaseModel):
        id: int
        qty: int = Field(ge=0)
        tags: list[str] = []

    return Row


def test_validate_records_partitions(load_exercise):
    m = load_exercise("ex05_bulk_validation")
    Row = make_model()
    valid, errors = m.validate_records(Row, [{"id": "1", "qty": 2}, {"id": "x", "qty": -1}, {"id": 3, "qty": 0, "tags": [1]}, {"id": 4, "qty": 5}])
    assert [r.id for r in valid] == [1, 4]
    assert [e["index"] for e in errors] == [1, 2]
    assert sorted(x["loc"] for x in errors[0]["errors"]) == ["id", "qty"] and errors[1]["errors"][0]["loc"] == "tags.0"
    assert {"loc", "type", "msg"} == set(errors[0]["errors"][0])
    assert m.validate_records(Row, []) == ([], [])


def test_validate_json_lines(load_exercise):
    m = load_exercise("ex05_bulk_validation")
    Row = make_model()
    text = '{"id": 1, "qty": 1}\n\n{"id": "x", "qty": 1}\nnao e json\n{"id": 5, "qty": 5}\n'
    valid, errors = m.validate_json_lines(Row, text)
    assert [r.id for r in valid] == [1, 5]
    assert [e["index"] for e in errors] == [3, 4]                                       # linhas 1-based, contando a vazia
    assert errors[0]["errors"][0]["type"] == "int_parsing" and errors[1]["errors"][0]["type"] == "json_invalid"
    assert errors[1]["errors"][0]["loc"] == ""


# ---------- ex06 ----------
def test_money_normalization(load_exercise):
    m = load_exercise("ex06_money")
    item = m.Item(name="x", price="9,90", qty=3)
    assert item.price == Decimal("9.90") and isinstance(item.price, Decimal)
    assert m.Item(name="x", price=0.1 + 0.2, qty=1).price == Decimal("0.30")
    assert m.Item(name="x", price=5, qty=1).price == Decimal("5.00")
    assert m.Item(name="x", price="2.675", qty=1).price == Decimal("2.68")            # meio-par: 2.675 -> 2.68 (o 7 é ímpar)
    assert m.Item(name="x", price="2.665", qty=1).price == Decimal("2.66")            # meio-par: 2.665 -> 2.66 (o 6 é par)
    for bad in (True, float("nan"), float("inf"), "abc", "-1", -3):
        with pytest.raises(ValidationError):
            m.Item(name="x", price=bad, qty=1)
    with pytest.raises(ValidationError):
        m.Item(name="x", price=1, qty=0)


def test_invoice_total_and_json(load_exercise):
    m = load_exercise("ex06_money")
    invoice = m.Invoice(items=[{"name": "a", "price": "9.90", "qty": 3}, {"name": "b", "price": "0.10", "qty": 1}], discount="5")
    assert invoice.total == Decimal("24.80")
    dumped = json.loads(invoice.model_dump_json())
    assert dumped["total"] == "24.80" and dumped["discount"] == "5.00" and dumped["items"][0]["price"] == "9.90"
    assert m.Invoice.model_validate_json(invoice.model_dump_json()).total == Decimal("24.80")
    assert m.Invoice(items=[{"name": "a", "price": 1, "qty": 1}]).discount == Decimal("0.00")


def test_invoice_validation(load_exercise):
    m = load_exercise("ex06_money")
    with pytest.raises(ValidationError):
        m.Invoice(items=[])
    with pytest.raises(ValidationError, match="desconto maior que o total"):
        m.Invoice(items=[{"name": "a", "price": 10, "qty": 1}], discount="11")
    assert m.Invoice(items=[{"name": "a", "price": 10, "qty": 1}], discount="10").total == Decimal("0.00")
