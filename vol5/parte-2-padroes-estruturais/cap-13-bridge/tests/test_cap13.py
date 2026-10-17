import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_channels(load_exercise):
    m = load_exercise("ex01_bridge_messages")
    assert m.EmailChannel().deliver("a@x.com", "oi") == "EMAIL <a@x.com>: oi"
    with pytest.raises(ValueError, match="endereço inválido: ana"):
        m.EmailChannel().deliver("ana", "oi")
    assert m.SmsChannel().deliver("+55", "oi") == "SMS +55: oi"
    with pytest.raises(ValueError, match="número inválido: 55"):
        m.SmsChannel().deliver("55", "oi")
    long = m.SmsChannel().deliver("+55", "x" * 200)
    assert long == "SMS +55: " + "x" * 159 + "…" and m.SmsChannel().deliver("+1", "y" * 160).endswith("y" * 160)
    console = m.ConsoleChannel()
    assert console.deliver("ops", "ok") == "CONSOLE ops: ok" and console.lines == ["ops: ok"]


def test_messages_and_bridge(load_exercise):
    m = load_exercise("ex01_bridge_messages")
    email, sms = m.EmailChannel(), m.SmsChannel()
    alert = m.AlertMessage(email)
    assert alert.channel is email and alert.send("a@x.com", "disco cheio") == "EMAIL <a@x.com>: [ALERTA] DISCO CHEIO"
    assert m.AlertMessage(sms).send("+55", "oi") == "SMS +55: [ALERTA] OI"
    report = m.ReportMessage(sms, "Vendas")
    assert report.send("+55", "R$ 10") == "SMS +55: Vendas\nR$ 10\n-- fim"
    assert m.ReminderMessage(email).send("a@x.com", "pagar a conta") == "EMAIL <a@x.com>: Pagar a conta (lembrete)"
    assert m.ReminderMessage(email).send("a@x.com", "ÉÉ") == "EMAIL <a@x.com>: ÉÉ (lembrete)"
    with pytest.raises(ValueError, match="corpo vazio"):
        m.ReminderMessage(email).send("a@x.com", "")
    with pytest.raises(TypeError):
        m.Message(email)                                                                      # abstrata


def test_with_channel_keeps_state(load_exercise):
    m = load_exercise("ex01_bridge_messages")
    console = m.ConsoleChannel()
    report = m.ReportMessage(m.EmailChannel(), "Título")
    moved = report.with_channel(console)
    assert moved is not report and type(moved) is m.ReportMessage and moved.title == "Título" and moved.channel is console
    assert report.channel is not console
    assert moved.send("ops", "corpo") == "CONSOLE ops: Título\ncorpo\n-- fim" and console.lines == ["ops: Título\ncorpo\n-- fim"]
    with pytest.raises(ValueError):
        report.send("sem-arroba", "x")                                                        # o original continua com o e-mail


# ---------- ex02 ----------
ROWS = [{"nome": "Ana", "nota": 9.5}, {"nome": 'Bia, "a"', "nota": 7}]


def test_csv_exporter(load_exercise):
    m = load_exercise("ex02_callable_bridge")
    out = []
    m.CsvExporter(out.append).export(ROWS)
    assert out == ["nome,nota", "Ana,9.5", '"Bia, ""a""",7']
    out2 = []
    m.CsvExporter(out2.append, delimiter=";").export([{"a": "x;y", "b": 1}])
    assert out2 == ["a;b", '"x;y";1']
    with pytest.raises(ValueError, match="sem linhas"):
        m.CsvExporter(out.append).export([])
    with pytest.raises(KeyError):
        m.CsvExporter(out.append).export([{"a": 1, "b": 2}, {"a": 3}])


def test_jsonl_and_table(load_exercise):
    m = load_exercise("ex02_callable_bridge")
    out = []
    m.JsonLinesExporter(out.append).export([{"b": 1, "a": "é"}, {"a": None, "b": [1]}])
    assert out == ['{"a": "é", "b": 1}', '{"a": null, "b": [1]}']
    table = []
    m.TableExporter(table.append).export([{"nome": "Ana", "idade": 30}, {"nome": "Beatriz", "idade": 5}])
    assert table == ["nome    | idade", "--------+------", "Ana     | 30", "Beatriz | 5"]
    for exporter in (m.JsonLinesExporter, m.TableExporter):
        with pytest.raises(ValueError, match="sem linhas"):
            exporter(out.append).export([])


def test_writers(load_exercise, tmp_path):
    m = load_exercise("ex02_callable_bridge")
    a, b = [], []
    w = m.fan_out(m.list_writer(a), m.prefixed(b.append, "> "))
    w("x")
    w("y")
    assert a == ["x", "y"] and b == ["> x", "> y"]
    with pytest.raises(ValueError, match="nenhum destino"):
        m.fan_out()
    sunk = []

    def boom(line):
        raise OSError("falhou")

    w2 = m.fan_out(boom, sunk.append, boom)
    with pytest.raises(OSError):
        w2("z")
    assert sunk == ["z"]
    path = tmp_path / "saida.txt"
    with m.FileWriter(path) as fw:
        m.CsvExporter(fw).export(ROWS)
    assert path.read_text(encoding="utf-8") == 'nome,nota\nAna,9.5\n"Bia, ""a""",7\n'
    with pytest.raises(ValueError, match="destino fechado"):
        fw("tarde demais")
    fw.close()                                                                                # fechar duas vezes não faz mal
    both = []
    with m.FileWriter(tmp_path / "dois.txt") as f2:
        m.TableExporter(m.fan_out(f2, both.append)).export([{"a": 1}])
    assert both == ["a", "-", "1"] and (tmp_path / "dois.txt").read_text(encoding="utf-8") == "a\n-\n1\n"


# ---------- ex03 ----------
def test_renderers(load_exercise):
    m = load_exercise("ex03_drawing_api")
    assert m.num(3) == "3" and m.num(2.5) == "2.5" and m.num(2.0) == "2"
    svg, text = m.SvgRenderer(), m.TextRenderer()
    assert svg.circle(1, 2, 3) == '<circle cx="1" cy="2" r="3"/>' and svg.rect(0, 0, 2.5, 4) == '<rect x="0" y="0" width="2.5" height="4"/>'
    assert text.circle(1, 2, 3) == "circle at (1, 2) radius 3" and text.rect(0, 0, 2.5, 4) == "rect at (0, 0) size 2.5x4"


def test_shapes_bridge(load_exercise):
    m = load_exercise("ex03_drawing_api")
    svg, text = m.SvgRenderer(), m.TextRenderer()
    c = m.Circle(svg, 1, 1, 2)
    r = m.Rectangle(text, 0, 0, 3, 4)
    assert c.draw() == '<circle cx="1" cy="1" r="2"/>' and r.draw() == "rect at (0, 0) size 3x4"
    assert abs(c.area() - 12.566370614359172) < 1e-9 and r.area() == 12
    s = c.scale(2.5)
    assert s is not c and s.r == 5.0 and s.draw() == '<circle cx="1" cy="1" r="5"/>' and c.r == 2
    assert r.scale(0.5).draw() == "rect at (0, 0) size 1.5x2"
    moved = c.with_renderer(text)
    assert moved is not c and moved.draw() == "circle at (1, 1) radius 2" and c.draw().startswith("<circle")
    for bad in (0, -1):
        with pytest.raises(ValueError, match="fator inválido"):
            c.scale(bad)
    with pytest.raises(ValueError, match="raio inválido"):
        m.Circle(svg, 0, 0, 0)
    with pytest.raises(ValueError, match="tamanho inválido"):
        m.Rectangle(svg, 0, 0, 1, 0)


def test_group(load_exercise):
    m = load_exercise("ex03_drawing_api")
    svg, text = m.SvgRenderer(), m.TextRenderer()
    g = m.Group(svg, [m.Circle(svg, 0, 0, 1), m.Rectangle(text, 1, 1, 2, 2)])
    assert g.draw() == '<circle cx="0" cy="0" r="1"/>\nrect at (1, 1) size 2x2'
    assert abs(g.area() - (3.141592653589793 + 4)) < 1e-9
    assert g.scale(2).draw() == '<circle cx="0" cy="0" r="2"/>\nrect at (1, 1) size 4x4'
    all_text = g.with_renderer(text)
    assert all_text.draw() == "circle at (0, 0) radius 1\nrect at (1, 1) size 2x2" and g.draw().startswith("<circle")
    assert m.Group(svg, []).draw() == "" and m.Group(svg, []).area() == 0
    nested = m.Group(svg, [g, m.Circle(svg, 5, 5, 1)])
    assert nested.draw().count("\n") == 2


# ---------- ex04 ----------
def test_counts(load_exercise):
    m = load_exercise("ex04_hierarchy_report")
    assert m.explosion_count(3, 4) == 12 and m.bridge_count(3, 4) == 9 and m.bridge_count(3, 4, bases=0) == 7
    assert m.savings(3, 4) == 3 and m.savings(2, 2) == -2 and m.savings(10, 6) == 60 - 18
    for fn in (m.explosion_count, m.bridge_count):
        with pytest.raises(ValueError, match="contagem negativa"):
            fn(-1, 2)
    pairs = m.worthwhile_pairs(5)
    assert pairs[0] == (2, 5) and (3, 3) in pairs and (2, 4) not in pairs and (1, 5) not in pairs
    assert pairs == sorted(pairs) and all(a <= b for a, b in pairs) and (5, 5) in pairs
    assert m.worthwhile_pairs(2) == [] and m.worthwhile_pairs(1) == []


def test_split_camel(load_exercise):
    m = load_exercise("ex04_hierarchy_report")
    assert m.split_camel("AlertEmail") == ["Alert", "Email"] and m.split_camel("SMSAlert") == ["SMS", "Alert"]
    assert m.split_camel("HttpRequest2") == ["Http", "Request2"] and m.split_camel("Alert") == ["Alert"] and m.split_camel("") == []
    assert m.split_camel("AlertEmailChannel") == ["Alert", "Email", "Channel"]


def test_cartesian_candidates(load_exercise):
    m = load_exercise("ex04_hierarchy_report")
    names = ["AlertEmail", "AlertSms", "ReportEmail", "ReportSms", "Logger", "ReminderEmail", "ReminderSms", "ReminderFax", "Config", "AlertEmail", "BaseAlertEmail"]
    assert m.cartesian_candidates(names) == [(("Alert", "Report"), ("Email", "Sms"))]
    more = names + ["AlertSlack", "ReportSlack"]
    assert m.cartesian_candidates(more) == [(("Alert", "Report"), ("Email", "Slack", "Sms")), ]
    assert m.cartesian_candidates(["AlertEmail", "ReportSms"]) == [] and m.cartesian_candidates([]) == []
    assert m.cartesian_candidates(["AlertEmail", "ReportEmail"]) == []                      # um só sufixo: não é produto cartesiano


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["bridge_classico", "bridge_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
