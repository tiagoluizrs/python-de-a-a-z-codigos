import copy
import datetime as dt
import subprocess
import sys
import threading
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def sample():
    return {"name": "base", "tags": ["a", "b"], "limits": {"max": 10}, "pair": ([1], [2]), "ids": {1, 2}}


def test_shared_mutables_shallow_and_deep(load_exercise):
    m = load_exercise("ex01_shallow_vs_deep")
    original = sample()
    assert m.shared_mutables(original, copy.copy(original)) == ["ids", "limits", "pair[0]", "pair[1]", "tags"]
    assert m.shared_mutables(original, copy.deepcopy(original)) == []
    assert m.is_independent(original, copy.deepcopy(original)) and not m.is_independent(original, copy.copy(original))


def test_shared_mutables_nested_paths(load_exercise):
    m = load_exercise("ex01_shallow_vs_deep")
    a = sample()
    b = copy.deepcopy(a)
    shared = a["limits"]
    b["limits"] = {"max": 10, "inner": shared}
    a["limits"] = {"max": 10, "inner": shared}
    assert m.shared_mutables(a, b) == ["limits.inner"]
    b = copy.deepcopy(a)
    b["pair"][1].append(3)
    b["pair"] = (a["pair"][0], b["pair"][1])
    assert m.shared_mutables(a, b) == ["pair[0]"]
    x = [1]
    assert m.shared_mutables(x, x) == ["."]
    assert m.shared_mutables("abc", "abc") == [] and m.shared_mutables(1, 1) == [] and m.shared_mutables((1, 2), (1, 2)) == []
    assert m.shared_mutables({"k": [1]}, {"k": (1,)}) == []


def test_make_grid(load_exercise):
    m = load_exercise("ex01_shallow_vs_deep")
    g = m.make_grid(2, 3, "x")
    assert g == [["x", "x", "x"], ["x", "x", "x"]]
    g[0][0] = "y"
    assert g[1][0] == "x"
    assert m.make_grid(0, 5) == [] and m.make_grid(2, 0) == [[], []]
    with pytest.raises(ValueError, match="dimensões negativas"):
        m.make_grid(-1, 2)


# ---------- ex02 ----------
def test_report_copy_and_deepcopy(load_exercise):
    m = load_exercise("ex02_custom_copy")
    r = m.Report("Relatório", ["intro", "dados"])
    assert r.render() == "Relatório: intro, dados"
    r.sections.append("fim")
    assert r.render() == "Relatório: intro, dados"                      # cache de propósito
    shallow = copy.copy(r)
    assert shallow is not r and shallow.sections is r.sections and shallow._lock is not r._lock and shallow._cache is None
    assert shallow.render() == "Relatório: intro, dados, fim"
    deep = copy.deepcopy(r)
    assert deep.sections == r.sections and deep.sections is not r.sections and deep._lock is not r._lock and deep._cache is None
    deep.sections.append("extra")
    assert "extra" not in r.sections
    assert isinstance(deep._lock, type(threading.Lock()))


def test_report_subclass_and_memo(load_exercise):
    m = load_exercise("ex02_custom_copy")

    class Special(m.Report):
        pass

    s = Special("t", ["a"])
    assert type(copy.copy(s)) is Special and type(copy.deepcopy(s)) is Special
    holder = [s, s]
    copied = copy.deepcopy(holder)
    assert copied[0] is copied[1] and copied[0] is not s                  # o memo preserva o compartilhamento
    cyc = m.Report("c", [])
    cyc.sections.append(cyc)
    twin = copy.deepcopy(cyc)
    assert twin.sections[0] is twin


def test_report_with_changes(load_exercise):
    m = load_exercise("ex02_custom_copy")
    r = m.Report("T", ["a"])
    r.render()
    v = r.with_changes(title="Novo")
    assert v.title == "Novo" and r.title == "T" and v.sections is r.sections and v._cache is None
    assert r.with_changes(sections=["z"]).sections == ["z"]
    with pytest.raises(AttributeError, match="Report não tem o atributo 'color'"):
        r.with_changes(color="red")
    with pytest.raises(AttributeError):
        r.with_changes(title="x", _lock=None)


# ---------- ex03 ----------
@dataclass
class Shape:
    kind: str
    points: list


def test_registry_basic(load_exercise):
    m = load_exercise("ex03_registry")
    reg = m.PrototypeRegistry()
    original = Shape("quadrado", [(0, 0)])
    reg.register("sq", original)
    original.points.append((1, 1))                                      # não afeta o protótipo guardado
    a = reg.create("sq")
    assert a == Shape("quadrado", [(0, 0)]) and a is not reg.create("sq")
    a.points.append((9, 9))
    assert reg.create("sq").points == [(0, 0)]
    b = reg.create("sq", kind="losango")
    assert b.kind == "losango" and reg.create("sq").kind == "quadrado"
    assert len(reg) == 1 and "sq" in reg and "x" not in reg and reg.names() == ["sq"]


def test_registry_errors(load_exercise):
    m = load_exercise("ex03_registry")
    reg = m.PrototypeRegistry()
    with pytest.raises(KeyError, match="protótipo desconhecido: x; disponíveis: nenhum"):
        reg.create("x")
    reg.register("b", Shape("b", []))
    reg.register("a", Shape("a", []))
    with pytest.raises(KeyError, match="disponíveis: a, b"):
        reg.create("zzz")
    with pytest.raises(ValueError, match="protótipo já registrado: a"):
        reg.register("a", Shape("a", []))
    with pytest.raises(ValueError, match="nome vazio"):
        reg.register("", Shape("a", []))
    with pytest.raises(AttributeError, match="'color' não é um atributo de Shape"):
        reg.create("a", color="red")
    assert reg.names() == ["a", "b"]
    reg.unregister("a")
    assert reg.names() == ["b"]
    with pytest.raises(KeyError):
        reg.unregister("a")


# ---------- ex04 ----------
@dataclass(frozen=True)
class Style:
    font: str = "serif"
    size: int = 12


def test_variant(load_exercise):
    m = load_exercise("ex04_variants")
    base = Style()
    assert m.variant(base, size=18) == Style(size=18) and base.size == 12
    P = namedtuple("P", "x y")
    assert m.variant(P(1, 2), y=9) == P(1, 9)
    assert m.variant(dt.date(2026, 10, 13), day=1) == dt.date(2026, 10, 1)
    with pytest.raises(TypeError):
        m.variant(base, color="red")
    assert m.variants(base, "size", [8, 10, 12]) == [Style(size=8), Style(size=10), Style(size=12)]
    assert m.variants(base, "font", []) == []


def test_copy_matrix(load_exercise):
    m = load_exercise("ex04_variants")
    src = [[1, 2], [3], []]
    out = m.copy_matrix(src)
    assert out == src and out is not src and all(a is not b for a, b in zip(out, src))
    out[0][0] = 99
    assert src[0][0] == 1
    with pytest.raises(TypeError, match=r"linha inválida: \(1, 2\)"):
        m.copy_matrix([[1], (1, 2)])
    assert m.copy_matrix([]) == []


def test_copy_json(load_exercise):
    m = load_exercise("ex04_variants")
    src = {"a": [1, 2.5, {"b": None, "c": True}], "d": "texto", "e": {}}
    out = m.copy_json(src)
    assert out == src and out is not src and out["a"] is not src["a"] and out["a"][2] is not src["a"][2]
    out["a"][2]["b"] = 5
    assert src["a"][2]["b"] is None
    assert m.copy_json(3) == 3 and m.copy_json("x") == "x" and m.copy_json(None) is None
    for bad, message in [({1, 2}, "tipo não suportado: set"), ((1,), "tipo não suportado: tuple"), ([object()], "tipo não suportado: object")]:
        with pytest.raises(TypeError, match=message):
            m.copy_json(bad)
    with pytest.raises(TypeError, match="chave inválida: 1"):
        m.copy_json({1: "x"})


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["prototype_classico", "prototype_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
