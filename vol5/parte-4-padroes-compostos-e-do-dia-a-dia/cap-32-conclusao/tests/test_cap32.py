import ast
import inspect
import json
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def code_lines(*objects):
    """Linhas de código normalizadas (``ast.unparse``), sem docstrings."""
    total = 0
    for obj in objects:
        tree = ast.parse(textwrap.dedent(inspect.getsource(obj)))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
                first = node.body[0]
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                    node.body = node.body[1:] or [ast.Pass()]
        total += len(ast.unparse(tree).splitlines())
    return total


# ---------- ex01 ----------
def test_strategy_as_functions(load_exercise):
    m = load_exercise("ex01_idioms")
    for total in (0, 1, 999, 1_000, 12_345):
        for p in (0, 10, 33, 100):
            assert m.percent(p)(total) == m.PercentDiscount(p).apply(total) == m.checkout_total(total, m.percent(p))
        for cents in (0, 500, 10_000):
            assert m.fixed(cents)(total) == m.FixedDiscount(cents).apply(total) == m.checkout_total(total, m.fixed(cents))
        assert m.no_discount(total) == m.NoDiscount().apply(total) == m.checkout_total(total) == m.Checkout().total(total)
    assert m.checkout_total(1_000, m.percent(10)) == 900 and m.checkout_total(100, m.fixed(500)) == 0
    assert inspect.isfunction(m.no_discount) and not inspect.isclass(m.percent) and callable(m.percent(5)) and not inspect.isclass(m.percent(5))
    assert code_lines(m.no_discount, m.percent, m.fixed, m.checkout_total) <= 10


def test_singleton_as_cached_function(load_exercise):
    m = load_exercise("ex01_idioms")
    config = m.get_config()
    assert config is m.get_config() and config == {"env": "dev", "debug": False} == m.ClassicConfig().values
    config["debug"] = True
    assert m.get_config()["debug"] is True                                   # é UMA instância compartilhada
    assert hasattr(m.get_config, "cache_clear")
    m.get_config.cache_clear()
    assert m.get_config() is not config and m.get_config()["debug"] is False
    assert code_lines(m.get_config) <= 4


def run_script(m, make_pairs, items):
    """Executa a mesma sequência de operações com o par (do, undo) e devolve os estados da lista."""
    history, states = [], []
    for kind in ("append 4", "remove", "append 5", "remove", "undo", "undo", "append 6", "undo", "undo", "undo"):
        if kind.startswith("append"):
            m.run(history, m.append_cmd(items, int(kind.split()[1])))
        elif kind == "remove":
            m.run(history, m.remove_first_cmd(items))
        else:
            m.undo(history)
        states.append(list(items))
    return states


def test_command_with_undo_pairs(load_exercise):
    m = load_exercise("ex01_idioms")
    classic_items, classic_states, history = [1, 2, 3], [], m.ClassicHistory()
    for kind in ("append 4", "remove", "append 5", "remove", "undo", "undo", "append 6", "undo", "undo", "undo"):
        if kind.startswith("append"):
            history.run(m.AppendCommand(classic_items, int(kind.split()[1])))
        elif kind == "remove":
            history.run(m.RemoveFirstCommand(classic_items))
        else:
            history.undo()
        classic_states.append(list(classic_items))
    assert run_script(m, None, [1, 2, 3]) == classic_states == [[1, 2, 3, 4], [2, 3, 4], [2, 3, 4, 5], [3, 4, 5], [2, 3, 4, 5], [2, 3, 4], [2, 3, 4, 6], [2, 3, 4], [1, 2, 3, 4], [1, 2, 3]]


def test_command_details(load_exercise):
    m = load_exercise("ex01_idioms")
    items = [1, 2]
    pair = m.append_cmd(items, 9)
    assert items == [1, 2] and len(pair) == 2 and all(callable(f) for f in pair)           # nada acontece até chamar o do
    pair[0]()
    assert items == [1, 2, 9]
    pair[1]()
    assert items == [1, 2]
    history = []
    with pytest.raises(IndexError):
        m.run(history, m.remove_first_cmd([]))
    assert history == []                                                                    # o do falhou: nada foi guardado
    with pytest.raises(LookupError, match="nada para desfazer"):
        m.undo([])
    m.run(history, m.append_cmd(items, 5))
    assert len(history) == 1 and isinstance(history, list)
    m.undo(history)
    assert history == [] and items == [1, 2]
    assert code_lines(m.append_cmd, m.remove_first_cmd, m.run, m.undo) <= 16


def test_iterators_as_generators(load_exercise):
    m = load_exercise("ex01_idioms")
    for n in (0, 1, 5):
        assert list(m.countdown(n)) == list(m.ClassicCountdown(n))
    c = m.countdown(3)
    assert iter(c) is c and next(c) == 3 and list(c) == [2, 1]
    assert next(m.countdown(10 ** 9)) == 10 ** 9                                            # preguiçoso
    with pytest.raises(ValueError, match="n negativo"):
        m.countdown(-1)                                                                      # na CHAMADA, antes de iterar
    for seq in ([], [1], [1, 2], [1, 2, 3, 4], "abc"):
        assert list(m.pairs(seq)) == list(m.ClassicPairs(seq))
    assert list(m.pairs(iter("abc"))) == [("a", "b"), ("b", "c")] and list(m.pairs(x for x in [])) == []
    consumed = []

    def source():
        for i in range(10):
            consumed.append(i)
            yield i

    first = next(iter(m.pairs(source())))
    assert first == (0, 1) and consumed == [0, 1]
    assert code_lines(m.countdown) <= 6 and code_lines(m.pairs) <= 5


def test_template_method_as_function(load_exercise):
    m = load_exercise("ex01_idioms")
    for rows in ([], ["a"], ["a", "b", "c"]):
        assert m.render_report(rows, **m.TEXT) == m.TextReport().render(rows)
        assert m.render_report(rows, **m.HTML) == m.HtmlReport().render(rows)
    assert m.render_report(["x", "y"], header=lambda rows: f"H{len(rows)}", line=str.upper, footer=lambda rows: "F") == "H2\nX\nY\nF"
    with pytest.raises(TypeError):
        m.render_report(["a"], m.TEXT["header"], m.TEXT["line"], m.TEXT["footer"])           # os passos são só por palavra-chave
    assert set(m.TEXT) == set(m.HTML) == {"header", "line", "footer"} and code_lines(m.render_report) <= 3


def test_factory_as_dictionary(load_exercise):
    m = load_exercise("ex01_idioms")
    assert set(m.SHAPES) == {"circle", "square", "rect"}
    for kind, args in (("circle", (2,)), ("square", (3,)), ("rect", (2, 5))):
        assert m.create(kind, *args) == m.ShapeFactory.create(kind, *args)
    with pytest.raises(ValueError) as info:
        m.create("hexagon", 1)
    assert str(info.value) == "forma desconhecida: 'hexagon'; disponíveis: circle, rect, square"
    m.SHAPES["triangle"] = lambda a, b, c: ("triângulo", a, b, c)                            # um tipo NOVO, sem editar create
    assert m.create("triangle", 3, 4, 5) == ("triângulo", 3, 4, 5)
    with pytest.raises(ValueError, match="disponíveis: circle, rect, square, triangle"):
        m.create("hexagon", 1)
    assert code_lines(m.create) <= 5


# ---------- ex02 ----------
def test_every_rule_triggers_its_entries(load_exercise):
    m = load_exercise("ex02_decision_guide")
    assert m.recommend(varies_algorithm=True) == ["Strategy: uma função"]
    assert m.recommend(undo_needed=True) == ["Command: o par (do, undo)", "Memento: estado imutável"]
    assert m.recommend(hide_storage=True) == ["Repository: uma coleção", "Unit of Work: @contextmanager"]
    for fact, pattern, form in m.RULES:
        assert f"{pattern}: {form}" in m.recommend(**{fact: True})
    assert len({fact for fact, _, _ in m.RULES}) == 26 and len(m.RULES) == 28


def test_order_follows_the_table_and_falsy_facts_are_ignored(load_exercise):
    m = load_exercise("ex02_decision_guide")
    result = m.recommend(need_fakes=True, traverse=True, hide_storage=True, notify_many=True, varies_algorithm=True)
    assert result == [
        "Strategy: uma função", "Observer: uma lista de funções", "Iterator: um gerador", "Repository: uma coleção",
        "Unit of Work: @contextmanager", "Injeção de Dependência: parâmetros e raiz de composição",
    ]
    assert m.recommend(varies_algorithm=False, notify_many=0, traverse=None, hide_storage="") == [m.NONE] and m.recommend() == [m.NONE]
    assert m.recommend(notify_many="sim", traverse=1) == ["Observer: uma lista de funções", "Iterator: um gerador"]


def test_unknown_facts_and_bad_variants(load_exercise):
    m = load_exercise("ex02_decision_guide")
    with pytest.raises(TypeError, match="fato desconhecido: alpha"):
        m.recommend(zeta=True, alpha=True)
    with pytest.raises(TypeError, match="fato desconhecido: strategy"):
        m.recommend(strategy=True)
    for bad in (-1, True, False, "2", 1.5):
        with pytest.raises(TypeError, match="variants precisa ser int"):
            m.recommend(varies_algorithm=True, variants=bad)
    assert m.recommend(variants=None, notify_many=True) == ["Observer: uma lista de funções"]


def test_rule_of_three(load_exercise):
    m = load_exercise("ex02_decision_guide")
    assert m.recommend(varies_algorithm=True, variants=1) == [m.LATER]
    assert m.recommend(varies_algorithm=True, variants=0) == [m.LATER]
    assert m.recommend(varies_algorithm=True, variants=2) == ["Strategy: uma função"]
    assert m.recommend(varies_algorithm=True, notify_many=True, variants=1) == ["Observer: uma lista de funções", m.LATER]
    assert m.recommend(notify_many=True, variants=1) == ["Observer: uma lista de funções"]            # nada adiado: sem o aviso
    assert m.recommend(variants=1) == [m.NONE] and m.recommend(variants=5) == [m.NONE]
    for fact in ("state_changes_behavior", "create_by_name", "product_families", "type_operations", "extensible_by_others"):
        assert m.recommend(**{fact: True, "variants": 1}) == [m.LATER]
        assert m.recommend(**{fact: True, "variants": 3}) != [m.LATER]
    assert m.recommend(wrap_behavior=True, absence_is_normal=True, variants=1) == ["Decorator: @decorador com functools.wraps", "Null Object: coleção vazia ou valor padrão"]


def test_singleton_becomes_injection(load_exercise):
    m = load_exercise("ex02_decision_guide")
    assert m.recommend(one_instance=True) == ["Singleton: o módulo"]
    assert m.recommend(one_instance=True, need_fakes=True) == ["Injeção de Dependência: parâmetros e raiz de composição"]
    assert m.recommend(need_fakes=True) == ["Injeção de Dependência: parâmetros e raiz de composição"]
    assert m.recommend(one_instance=True, need_fakes=False) == ["Singleton: o módulo"]
    assert m.recommend(one_instance=True, need_fakes=True, notify_many=True) == ["Observer: uma lista de funções", "Injeção de Dependência: parâmetros e raiz de composição"]


# ---------- ex03 ----------
SALES_DATA = [
    (1, "Ana", "BR", 12_000, True), (2, "Bia", "BR", 4_500, False), (3, "Caio", "PT", 30_000, False),
    (4, "Duda", "US", 9_900, True), (5, "Edu", "BR", 25_000, False), (6, "Fabi", "PT", 800, False),
]


def sales(m):
    return [m.Sale(*row) for row in SALES_DATA]


def test_formats_are_registered_and_render(load_exercise):
    m = load_exercise("ex03_capstone")
    assert m.formats.names() == ["csv", "json", "text"]
    rows = sales(m)[:2]
    assert m.to_csv(rows) == "id,cliente,valor\n1,Ana,120.00\n2,Bia,45.00" and m.to_csv([]) == "id,cliente,valor"
    assert json.loads(m.to_json(rows)) == [{"id": 1, "cliente": "Ana", "valor": 120.0}, {"id": 2, "cliente": "Bia", "valor": 45.0}] and m.to_json([]) == "[]"
    assert m.to_text(rows) == "Ana R$ 120.00; Bia R$ 45.00" and m.to_text([]) == ""
    assert m.formats.get("csv") is m.to_csv and m.formats.get("json") is m.to_json and m.formats.get("text") is m.to_text
    assert "ç" not in m.to_json([m.Sale(9, "Zoé", "BR", 1)]) and "Zoé" in m.to_json([m.Sale(9, "Zoé", "BR", 1)])


def test_generate_filters_orders_and_reports(load_exercise):
    m = load_exercise("ex03_capstone")
    service = m.build_service("test", sales(m))
    big = m.Spec(lambda s: s.amount_cents >= 10_000, "grande")
    br = m.Spec(lambda s: s.country == "BR", "BR")
    result = service.generate("csv", where=big & ~m.Spec(lambda s: s.vip, "vip"), order_by="amount")
    assert result == {"format": "csv", "count": 2, "content": "id,cliente,valor\n3,Caio,300.00\n5,Edu,250.00", "at": "2026-01-01T12:00:00"}
    assert service.generate("text", where=br | big, order_by="customer")["content"] == "Ana R$ 120.00; Bia R$ 45.00; Caio R$ 300.00; Edu R$ 250.00"
    assert service.generate("text", where=lambda s: s.amount_cents < 1_000)["content"] == "Fabi R$ 8.00"
    assert service.generate("json", where=lambda s: False)["count"] == 0
    assert [s["id"] for s in json.loads(service.generate("json")["content"])] == [1, 2, 3, 4, 5, 6]


def test_progress_and_logger(load_exercise):
    m = load_exercise("ex03_capstone")
    service = m.build_service("test", sales(m))
    events = []
    service.progress.connect(lambda i, n: events.append((i, n)))
    service.generate("csv", where=lambda s: s.country == "PT")
    assert events == [(1, 2), (2, 2)] and service.logger.lines == [("info", "gerado csv: 2 linhas")]
    events.clear()
    service.generate("csv", where=lambda s: False)
    assert events == [] and service.logger.lines[-1] == ("info", "gerado csv: 0 linhas")


def test_failures_are_checked_before_reading_and_logged(load_exercise):
    m = load_exercise("ex03_capstone")
    repo = m.InMemorySales(sales(m))
    logger = m.RecordingLogger()
    service = m.ReportService(repo, m.formats, lambda: m.FIXED, logger)
    with pytest.raises(KeyError, match="formato desconhecido: 'xml'; disponíveis: csv, json, text"):
        service.generate("xml", order_by="nada")                                             # o formato é conferido primeiro
    with pytest.raises(ValueError) as info:
        service.generate("csv", order_by="nada")
    assert str(info.value) == "ordenação desconhecida: 'nada'; disponíveis: amount, customer, id"
    assert repo.reads == 0 and logger.lines == []
    boom = m.Registry("formato")

    @boom.register("broken")
    def broken(rows):
        raise RuntimeError("explodiu")

    failing = m.ReportService(repo, boom, lambda: m.FIXED, logger)
    with pytest.raises(RuntimeError, match="explodiu"):
        failing.generate("broken")
    assert logger.lines == [("error", "falhou broken: RuntimeError")] and repo.reads == 1


def test_defaults_are_null_objects_and_independent(load_exercise):
    m = load_exercise("ex03_capstone")
    plain = m.ReportService(m.InMemorySales(sales(m)), m.formats, lambda: m.FIXED)
    assert plain.logger is m.NULL_LOGGER and isinstance(plain.progress, m.Signal)
    assert plain.generate("text", where=lambda s: s.id == 1)["content"] == "Ana R$ 120.00"
    other = m.ReportService(m.InMemorySales(sales(m)), m.formats, lambda: m.FIXED)
    assert other.progress is not plain.progress
    seen = []
    plain.progress.connect(lambda i, n: seen.append(i))
    other.generate("csv")
    assert seen == []

    class FalsyLogger(m.RecordingLogger):
        def __len__(self):
            return 0

    logger, signal = FalsyLogger(), m.Signal()
    assert not logger
    used = m.ReportService(m.InMemorySales(sales(m)), m.formats, lambda: m.FIXED, logger, signal)
    assert used.logger is logger and used.progress is signal


def test_composition_root(load_exercise):
    m = load_exercise("ex03_capstone")
    test = m.build_service("test", sales(m))
    assert isinstance(test.logger, m.RecordingLogger) and test.clock() == m.FIXED and test.formats is m.formats
    prod = m.build_service("prod", sales(m))
    assert prod.logger is m.NULL_LOGGER and isinstance(prod.generate("csv")["at"], str) and prod.clock == datetime.now
    assert prod.repo.all()[0].customer == "Ana"
    with pytest.raises(ValueError, match="ambiente desconhecido: 'dev'"):
        m.build_service("dev", [])
    assert m.build_service("test", []).generate("text")["content"] == ""


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["padroes_juntos", "mapa_do_volume"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()


def test_volume_map_is_consistent():
    r = subprocess.run([sys.executable, "-c", "import mapa_do_volume as m; print(m.check_coverage(), dict(m.by_family()), dict(m.gof_verdicts()))"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "30 {'criação': 6, 'estrutural': 7, 'comportamental': 11, 'composto': 1, 'do dia a dia': 5} {'simplificado': 12, 'embutido': 6, 'igual': 5}"
