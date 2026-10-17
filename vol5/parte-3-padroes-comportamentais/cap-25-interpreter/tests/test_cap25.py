import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def run(m, text, **ctx):
    return m.parse(text).interpret(ctx)


def test_compare_and_literals(load_exercise):
    m = load_exercise("ex01_rule_language")
    assert set(m.Compare.OPS) == {"==", "!=", "<", "<=", ">", ">="}
    assert run(m, "1 < 2") is True and run(m, "3 >= 3") is True and run(m, "3 > 3") is False
    assert run(m, "'a' == 'a'") is True and run(m, '"a" != \'b\'') is True and run(m, "2.5 > 2") is True
    assert run(m, "x != 3", x=4) is True and run(m, "x <= 3", x=4) is False
    assert m.parse("7").interpret({}) == 7 and m.parse("'oi'").interpret({}) == "oi" and m.parse("true").interpret({}) is True and m.parse("false").interpret({}) is False


def test_precedence_and_parentheses(load_exercise):
    m = load_exercise("ex01_rule_language")
    assert run(m, "true and not false") is True
    assert run(m, "not true or true") is True                 # (not true) or true
    assert run(m, "not (true or true)") is False
    assert run(m, "true or false and false") is True          # and amarra mais forte que or
    assert run(m, "(true or false) and false") is False
    assert run(m, "not not true") is True and run(m, "not 1 < 2") is False
    assert run(m, "((1 < 2))") is True


def test_business_rule(load_exercise):
    m = load_exercise("ex01_rule_language")
    rule = "age >= 18 and (country == 'BR' or vip) and not banned"
    base = {"age": 20, "country": "PT", "vip": True, "banned": False}
    assert run(m, rule, **base) is True
    assert run(m, rule, **{**base, "banned": True}) is False
    assert run(m, rule, **{**base, "age": 17}) is False
    assert run(m, rule, **{**base, "vip": False}) is False and run(m, rule, **{**base, "vip": False, "country": "BR"}) is True


def test_variables_and_errors(load_exercise):
    m = load_exercise("ex01_rule_language")
    assert m.parse("a and b or not c").variables() == frozenset("abc")
    assert m.parse("1 < 2").variables() == frozenset() and m.parse("my_var > 3 or my_var < 0").variables() == frozenset({"my_var"})
    with pytest.raises(KeyError, match="variável indefinida: idade"):
        run(m, "idade > 18")
    with pytest.raises(TypeError, match="não comparável: 'a' < 3"):
        run(m, "name < 3", name="a")


def test_short_circuit_and_bool_results(load_exercise):
    m = load_exercise("ex01_rule_language")
    assert run(m, "false and ghost") is False and run(m, "true or ghost") is True
    with pytest.raises(KeyError):
        run(m, "true and ghost")
    with pytest.raises(KeyError):
        run(m, "false or ghost")
    assert run(m, "x or y", x=0, y=5) is True and run(m, "x and y", x=3, y=0) is False and run(m, "not x", x=[]) is True
    tree = m.And(m.Literal(True), m.Variable("x"))
    assert tree.interpret({"x": False}) is False and tree.variables() == frozenset({"x"})
    assert m.Or(m.Literal(False), m.Not(m.Variable("y"))).interpret({"y": 0}) is True


@pytest.mark.parametrize(
    "text, message",
    [
        ("age >=", "esperava um valor, veio None"),
        ("age >= 18 )", "sobrou texto"),
        ("age @ 3", "posição 4"),
        ("(1 < 2", "faltou fechar"),
        ("and", "esperava um valor"),
        ("1 2", "sobrou texto"),
        ("", "esperava um valor"),
    ],
)
def test_syntax_errors(load_exercise, text, message):
    m = load_exercise("ex01_rule_language")
    with pytest.raises(SyntaxError, match=message):
        m.parse(text)


# ---------- ex02 ----------
def test_safe_eval_arithmetic_and_logic(load_exercise):
    m = load_exercise("ex02_safe_eval")
    s = m.safe_eval
    assert s("1 + 2 * 3") == 7 and s("2 ** 10") == 1024 and s("7 // 2") == 3 and s("7 % 4") == 3 and s("7 / 2") == 3.5
    assert s("-x + 1", {"x": 4}) == -3 and s("+5") == 5 and s("True + 1") == 2 and s(" 1 + 1 ") == 2
    assert s("0 or 'x'") == "x" and s("'' or 0") == 0 and s("1 and 2") == 2 and s("0 and 2") == 0 and s("not 0") is True
    assert s("2 ** 100") == 2 ** 100 and s("2 ** -3") == 0.125
    assert s("x", {"x": 7}) == 7 and s("1") == 1 and s("None") is None and s("'oi'") == "oi" and s("2.5") == 2.5


def test_safe_eval_comparisons_and_containers(load_exercise):
    m = load_exercise("ex02_safe_eval")
    s = m.safe_eval
    assert s("18 <= age < 65", {"age": 30}) is True and s("18 <= age < 65", {"age": 70}) is False and s("18 <= age < 65", {"age": 10}) is False
    assert s("x in (1, 2)", {"x": 2}) is True and s("x not in [1, 2]", {"x": 3}) is True and s("'a' in 'abc'") is True and s("1 == 1.0") is True
    assert s("(1, 2)") == (1, 2) and s("[1, 2]") == [1, 2] and s("{1, 2}") == {1, 2} and s("()") == ()
    assert s("country in ('BR', 'PT') and age >= 18", {"country": "PT", "age": 20}) is True


def test_safe_eval_variables(load_exercise):
    m = load_exercise("ex02_safe_eval")
    with pytest.raises(KeyError, match="variável indefinida: y"):
        m.safe_eval("x + y", {"x": 1})
    with pytest.raises(KeyError, match="variável indefinida: len"):
        m.safe_eval("len")
    assert m.safe_eval("len", {"len": 5}) == 5


@pytest.mark.parametrize(
    "text, node",
    [
        ("__import__('os').getcwd()", "Call"),
        ("().__class__", "Attribute"),
        ("x.y", "Attribute"),
        ("a[0]", "Subscript"),
        ("lambda: 1", "Lambda"),
        ("[x for x in y]", "ListComp"),
        ("f'{a}'", "JoinedStr"),
        ("1 if x else 2", "IfExp"),
        ("(y := 3)", "NamedExpr"),
        ("a is b", "Is"),
        ("a is not b", "IsNot"),
        ("b'abc'", "Constant"),
        ("1j", "Constant"),
        ("...", "Constant"),
        ("{'a': 1}", "Dict"),
        ("~5", "Invert"),
        ("'a' @ 'b'", "MatMult"),
    ],
)
def test_safe_eval_rejects(load_exercise, text, node):
    m = load_exercise("ex02_safe_eval")
    with pytest.raises(ValueError, match=f"expressão não permitida: {node}$"):
        m.safe_eval(text, {"a": 1, "b": 2, "x": 1, "y": [1]})


def test_safe_eval_validates_whole_tree_before_running(load_exercise):
    m = load_exercise("ex02_safe_eval")
    with pytest.raises(ValueError, match="Call"):
        m.safe_eval("False and open('x')")
    with pytest.raises(ValueError, match="Call"):
        m.safe_eval("x or __import__('os')", {"x": 1})
    with pytest.raises(ValueError, match="Call"):
        m.safe_eval("y + f()")                                 # nem chega a procurar a variável y


def test_safe_eval_limits_and_syntax(load_exercise):
    m = load_exercise("ex02_safe_eval")
    for text in ("2 ** 101", "2 ** -101", "9 ** 1000000"):
        with pytest.raises(ValueError, match="expoente grande demais"):
            m.safe_eval(text)
    for text in ("'a' * 3", "'a' + 'b'", "[1] + [2]", "-'a'", "x * 2"):
        with pytest.raises(ValueError, match="operandos devem ser números"):
            m.safe_eval(text, {"x": "t"})
    with pytest.raises(ZeroDivisionError):
        m.safe_eval("1 / 0")
    for text in ("1 +", "", "(", "x = 1"):
        with pytest.raises(ValueError, match="sintaxe inválida"):
            m.safe_eval(text)
    with pytest.raises(ValueError, match="expressão grande demais"):
        m.safe_eval("1+" * 600 + "1")
    assert m.safe_eval("1+" * 400 + "1") == 401


# ---------- ex03 ----------
def test_compile_expr_basics(load_exercise):
    m = load_exercise("ex03_rule_engine")
    fn, names = m.compile_expr("age >= 18 and country in ('BR', 'PT')")
    assert names == frozenset({"age", "country"})
    assert fn({"age": 20, "country": "PT"}) is True and fn({"age": 20, "country": "US"}) is False and fn({"age": 10, "country": "PT"}) is False
    fn, names = m.compile_expr("2 * x + 1 - y")
    assert fn({"x": 3, "y": 2}) == 5 and names == frozenset({"x", "y"})
    assert m.compile_expr("-x")[0]({"x": 4}) == -4 and m.compile_expr("not x")[0]({"x": 0}) is True
    assert m.compile_expr("1")[1] == frozenset()


def test_compile_expr_semantics(load_exercise):
    m = load_exercise("ex03_rule_engine")
    c = lambda text: m.compile_expr(text)[0]
    assert c("x or 'padrão'")({"x": ""}) == "padrão" and c("x and y")({"x": 3, "y": 0}) == 0 and c("x or y")({"x": 3}) == 3     # curto-circuito: y nem é lido
    assert c("18 <= a < 65")({"a": 30}) is True and c("18 <= a < 65")({"a": 65}) is False
    assert c("[1, x]")({"x": 2}) == (1, 2) and c("x not in (1, 2)")({"x": 3}) is True
    with pytest.raises(KeyError, match="variável indefinida: y"):
        c("x + y")({"x": 1})


@pytest.mark.parametrize(
    "text, node",
    [
        ("__import__('os')", "Call"),
        ("x.y", "Attribute"),
        ("x / 2", "Div"),
        ("x // 2", "FloorDiv"),
        ("x % 2", "Mod"),
        ("x ** 2", "Pow"),
        ("lambda: 1", "Lambda"),
        ("a is b", "Is"),
        ("a[0]", "Subscript"),
        ("b'x'", "Constant"),
    ],
)
def test_compile_expr_rejects_at_compile_time(load_exercise, text, node):
    m = load_exercise("ex03_rule_engine")
    with pytest.raises(ValueError, match=f"expressão não permitida: {node}$"):
        m.compile_expr(text)
    with pytest.raises(ValueError, match="sintaxe inválida"):
        m.compile_expr("1 +")


def test_compiled_function_does_not_parse_again(load_exercise, monkeypatch):
    m = load_exercise("ex03_rule_engine")
    fn, _ = m.compile_expr("a + b * 2")

    def boom(*args, **kwargs):
        raise AssertionError("não deve analisar de novo")

    monkeypatch.setattr(m.ast, "parse", boom)
    assert fn({"a": 1, "b": 3}) == 7 and fn({"a": 0, "b": 0}) == 0


def test_rule(load_exercise):
    m = load_exercise("ex03_rule_engine")
    r = m.Rule("adulto", "age >= 18")
    assert (r.name, r.expression, r.variables) == ("adulto", "age >= 18", frozenset({"age"}))
    assert r.matches({"age": 20}) is True and r.matches({"age": 3}) is False
    assert m.Rule("sempre", "1").matches({}) is True and m.Rule("nunca", "0").matches({}) is False
    for name in ("", "   "):
        with pytest.raises(ValueError, match="nome vazio"):
            m.Rule(name, "1")
    with pytest.raises(ValueError, match="Call"):
        m.Rule("ruim", "f()")


def test_engine_evaluate(load_exercise):
    m = load_exercise("ex03_rule_engine")
    e = m.RuleEngine()
    assert len(e) == 0 and e.needed_variables() == frozenset() and e.evaluate({}) == {"matched": [], "errors": {}}
    e.add("adulto", "age >= 18")
    e.add("brasileiro", "country == 'BR'")
    e.add("vip_ou_adulto", "vip or age >= 18")
    e.add("sempre", "1 < 2")
    assert len(e) == 4 and e.needed_variables() == frozenset({"age", "country", "vip"})
    assert e.evaluate({"age": 20, "country": "BR", "vip": False}) == {"matched": ["adulto", "brasileiro", "vip_ou_adulto", "sempre"], "errors": {}}
    assert e.evaluate({"age": 10, "country": "PT", "vip": False})["matched"] == ["sempre"]


def test_engine_errors_are_isolated(load_exercise):
    m = load_exercise("ex03_rule_engine")
    e = m.RuleEngine()
    e.add("a", "x > 1 and y > 1 and z > 1")
    e.add("b", "x > 1")
    e.add("c", "name < 3")
    e.add("d", "w or x")
    result = e.evaluate({"x": 5, "name": "ana"})
    assert result["matched"] == ["b"]
    assert result["errors"]["a"] == "variável indefinida: y"                 # a primeira que falta, em ordem alfabética
    assert result["errors"]["d"] == "variável indefinida: w"                 # mesmo com o curto-circuito dispensando
    assert result["errors"]["c"].startswith("TypeError: ") and set(result["errors"]) == {"a", "c", "d"}


def test_engine_add_remove(load_exercise):
    m = load_exercise("ex03_rule_engine")
    e = m.RuleEngine()
    rule = e.add("a", "1")
    assert isinstance(rule, m.Rule)
    with pytest.raises(ValueError, match="regra já existe: a"):
        e.add("a", "2")
    with pytest.raises(ValueError):
        e.add("b", "f()")
    assert len(e) == 1
    e.remove("a")
    assert len(e) == 0
    with pytest.raises(LookupError):
        e.remove("a")
    e.add("a", "2")                                                          # o nome volta a estar livre


# ---------- ex04 ----------
def test_rpn_operators(load_exercise):
    m = load_exercise("ex04_rpn_calculator")
    r = m.rpn
    assert r("3 4 + 2 *") == 14 and r("10 4 -") == 6 and r("7 2 //") == 3 and r("7 2 %") == 1 and r("2 10 **") == 1024 and r("7 2 /") == 3.5
    assert r("3 9 max") == 9 and r("3 9 min") == 3 and r("-5 abs") == 5 and r("5 neg") == -5 and r("1.5 2 *") == 3.0
    assert r("3 dup *") == 9 and r("1 2 swap -") == 1 and r("1 2 drop") == 1 and r("1 2 over + +") == 4
    assert isinstance(r("6 3 /"), float) and isinstance(r("6 3 +"), int)


def test_rpn_variables_and_words(load_exercise):
    m = load_exercise("ex04_rpn_calculator")
    assert m.rpn("x 2 ** y +", {"x": 3, "y": 1}) == 10
    words = {"sq": "dup *", "cube": "dup sq *"}
    assert m.rpn("5 sq 1 +", words=words) == 26 and m.rpn("3 cube", words=words) == 27
    assert m.rpn("1 2 +", words={"+": "drop"}) == 3                              # o operador embutido vence a palavra
    assert m.rpn("v", {"v": 1}, {"v": "10"}) == 10                               # a palavra vence a variável


def test_rpn_errors(load_exercise):
    m = load_exercise("ex04_rpn_calculator")
    for text, token in (("+", "+"), ("1 +", "+"), ("neg", "neg"), ("dup", "dup"), ("1 swap", "swap"), ("drop", "drop"), ("1 over", "over")):
        with pytest.raises(ValueError, match=f"pilha vazia em: {re.escape(token)}$"):
            m.rpn(text)
    with pytest.raises(ValueError, match="palavra desconhecida: foo"):
        m.rpn("1 foo")
    with pytest.raises(ValueError, match="expressão vazia"):
        m.rpn("")
    with pytest.raises(ValueError, match="expressão vazia"):
        m.rpn("1 drop")
    with pytest.raises(ValueError, match="sobraram valores na pilha"):
        m.rpn("1 2")
    with pytest.raises(ZeroDivisionError):
        m.rpn("1 0 /")


def test_rpn_recursion_limit(load_exercise):
    m = load_exercise("ex04_rpn_calculator")
    with pytest.raises(ValueError, match="recursão demais"):
        m.rpn("a", words={"a": "b", "b": "a"})
    ok = {"w0": "1", **{f"w{i}": f"w{i - 1}" for i in range(1, 50)}}
    assert m.rpn("w49", words=ok) == 1
    too_deep = {"w0": "1", **{f"w{i}": f"w{i - 1}" for i in range(1, 51)}}
    with pytest.raises(ValueError, match="recursão demais"):
        m.rpn("w50", words=too_deep)


def test_rpn_trace(load_exercise):
    m = load_exercise("ex04_rpn_calculator")
    assert m.rpn_trace("3 4 + 2 *") == [[3], [3, 4], [7], [7, 2], [14]]
    assert m.rpn_trace("5 sq 1 +", words={"sq": "dup *"}) == [[5], [25], [25, 1], [26]]
    assert m.rpn_trace("1 2") == [[1], [1, 2]] and m.rpn_trace("") == []
    steps = m.rpn_trace("1 2 3")
    assert steps[0] == [1] and steps[1] == [1, 2]                                # cópias: não mudam depois
    with pytest.raises(ValueError, match="pilha vazia em: \\+"):
        m.rpn_trace("+")
    assert m.rpn_trace("x", {"x": 9}) == [[9]]


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["interpreter_classico", "interpreter_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
