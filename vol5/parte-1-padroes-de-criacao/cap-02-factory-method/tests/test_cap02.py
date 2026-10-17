import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_parsers(load_exercise):
    m = load_exercise("ex01_simple_factory")
    assert m.parse("a,b\n1,2\n3,4\n", "csv") == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
    assert m.parse('[{"x": 1}, {"x": 2}]', "json") == [{"x": 1}, {"x": 2}]
    assert m.parse("um\n\n  dois  \n", "lines") == [{"line": "um"}, {"line": "dois"}]
    with pytest.raises(ValueError, match="json deve ser uma lista"):
        m.parse('{"x": 1}', "json")


def test_make_parser_lookup_and_errors(load_exercise):
    m = load_exercise("ex01_simple_factory")
    assert m.make_parser("  CSV ") is m.PARSERS["csv"]
    assert set(m.PARSERS) >= {"csv", "json", "lines"}
    with pytest.raises(ValueError) as info:
        m.make_parser("xml")
    assert str(info.value) == "formato desconhecido: 'xml'; disponíveis: csv, json, lines"


def test_register_parser(load_exercise):
    m = load_exercise("ex01_simple_factory")
    snapshot = dict(m.PARSERS)
    try:
        @m.register_parser("Upper")
        def parse_upper(text):
            return [{"line": text.upper()}]

        assert parse_upper("a") == [{"line": "A"}]
        assert m.parse("abc", "upper") == [{"line": "ABC"}]
        with pytest.raises(ValueError, match="formato já registrado: upper"):
            m.register_parser("UPPER")(lambda t: [])
        with pytest.raises(ValueError) as info:
            m.make_parser("zzz")
        assert "disponíveis: csv, json, lines, upper" in str(info.value)
    finally:
        m.PARSERS.clear()
        m.PARSERS.update(snapshot)


# ---------- ex02 ----------
def test_temperature_constructors(load_exercise):
    m = load_exercise("ex02_alt_constructors")
    assert m.Temperature.from_fahrenheit(212).celsius == pytest.approx(100.0)
    assert m.Temperature.from_kelvin(273.15).celsius == pytest.approx(0.0)
    t = m.Temperature(25.0)
    assert t.fahrenheit == pytest.approx(77.0) and t.kelvin == pytest.approx(298.15)


def test_temperature_cls_and_validation(load_exercise):
    m = load_exercise("ex02_alt_constructors")
    assert type(m.RoomTemperature.from_kelvin(300)) is m.RoomTemperature
    assert type(m.RoomTemperature.from_fahrenheit(70)) is m.RoomTemperature
    assert type(m.RoomTemperature.parse("20C")) is m.RoomTemperature
    for bad in (lambda: m.Temperature(-300), lambda: m.Temperature.from_kelvin(-1), lambda: m.Temperature.from_fahrenheit(-500)):
        with pytest.raises(ValueError, match="abaixo do zero absoluto"):
            bad()
    assert m.Temperature(-273.15).celsius == -273.15


@pytest.mark.parametrize("text,celsius", [("21.5C", 21.5), ("70 F", 21.1111111), ("300k", 26.85), ("  -5 c ", -5.0), ("0K", -273.15)])
def test_temperature_parse(load_exercise, text, celsius):
    m = load_exercise("ex02_alt_constructors")
    assert m.Temperature.parse(text).celsius == pytest.approx(celsius, abs=1e-6)


@pytest.mark.parametrize("bad", ["", "21", "C", "21 X", "abc", "1.2.3C", "21CC"])
def test_temperature_parse_invalid(load_exercise, bad):
    m = load_exercise("ex02_alt_constructors")
    with pytest.raises(ValueError, match="temperatura inválida"):
        m.Temperature.parse(bad)


# ---------- ex03 ----------
ROWS = [{"name": "Ana", "age": 30}, {"name": "Bia", "age": 25}]


def test_exporters(load_exercise):
    m = load_exercise("ex03_creator")
    assert m.CsvExporter().export(ROWS) == "name,age\nAna,30\nBia,25\n"
    assert m.JsonExporter().export(ROWS) == '[{"name": "Ana", "age": 30}, {"name": "Bia", "age": 25}]'
    assert m.JsonExporter().export([{"c": "é"}]) == '[{"c": "é"}]'


def test_column_order_and_errors(load_exercise):
    m = load_exercise("ex03_creator")
    rows = [{"b": 1, "a": 2}, {"a": 4, "b": 3}]
    assert m.CsvExporter().export(rows) == "b,a\n1,2\n3,4\n"
    with pytest.raises(ValueError, match="sem linhas"):
        m.CsvExporter().export([])
    with pytest.raises(KeyError):
        m.CsvExporter().export([{"a": 1, "b": 2}, {"a": 3}])
    with pytest.raises(TypeError):
        m.Exporter()                                     # abstrata


def test_factory_method_called_once_and_function_equivalence(load_exercise):
    m = load_exercise("ex03_creator")
    calls = []

    class Counting(m.Exporter):
        def create_writer(self):
            calls.append(1)
            return m.CsvWriter()

    assert Counting().export(ROWS) == "name,age\nAna,30\nBia,25\n"
    assert len(calls) == 1
    assert m.export_with(m.JsonWriter, ROWS) == m.JsonExporter().export(ROWS)
    assert m.export_with(lambda: m.CsvWriter(), ROWS) == m.CsvExporter().export(ROWS)
    assert Counting().export(ROWS) == m.export_with(m.CsvWriter, ROWS)


def test_writers_directly(load_exercise):
    m = load_exercise("ex03_creator")
    w = m.CsvWriter()
    w.write_header(["x", "y"])
    w.write_row(["a,b", 'c"d'])
    assert w.result() == 'x,y\n"a,b","c""d"\n'
    j = m.JsonWriter()
    j.write_header(["x"])
    j.write_row([1])
    j.write_row([2])
    assert j.result() == '[{"x": 1}, {"x": 2}]'


# ---------- ex04 ----------
class Server:
    def __init__(self, host, port=80, tags=None):
        self.host, self.port, self.tags = host, port, tags if tags is not None else []


class Loose:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_factory_for(load_exercise):
    m = load_exercise("ex04_factory_defaults")
    make = m.factory_for(Server, host="localhost", tags=["base"])
    a, b = make(), make(port=8080)
    assert (a.host, a.port, a.tags) == ("localhost", 80, ["base"]) and b.port == 8080
    a.tags.append("x")
    assert b.tags == ["base"] and make().tags == ["base"]
    assert make.cls is Server
    make.defaults["host"] = "mudou"
    make.defaults["tags"].append("zzz")
    assert make().host == "localhost" and make().tags == ["base"]
    shared = ["meu"]
    assert make(tags=shared).tags is shared


def test_factory_for_validation(load_exercise):
    m = load_exercise("ex04_factory_defaults")
    with pytest.raises(TypeError, match="Server não aceita o argumento 'color'"):
        m.factory_for(Server, color="red")
    make = m.factory_for(Server, host="h")
    with pytest.raises(TypeError, match="Server não aceita o argumento 'color'"):
        make(color="red")
    loose = m.factory_for(Loose, a=1)
    assert loose(b=2).kwargs == {"a": 1, "b": 2}


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["factory_method_classico", "factory_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
