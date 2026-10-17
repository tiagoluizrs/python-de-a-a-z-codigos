import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def users(m):
    return {
        "ana": m.User(1, "Ana", 30, "BR", ("vip",)),
        "bia": m.User(2, "Bia", 17, "BR"),
        "caio": m.User(3, "Caio", 45, "PT", banned=True),
        "duda": m.User(4, "Duda", 22, "US", ("vip",)),
        "edu": m.User(5, "Edu", 19, "PT", banned=None),
        "ze": m.User(6, "Zé", 16, "US", banned=True),
    }


def test_leaf_specs(load_exercise):
    m = load_exercise("ex01_classic_specs")
    u = users(m)
    assert m.AgeAtLeast(18).is_satisfied_by(u["ana"]) and m.AgeAtLeast(30).is_satisfied_by(u["ana"]) and not m.AgeAtLeast(31).is_satisfied_by(u["ana"])
    assert m.FromCountry("BR", "PT").is_satisfied_by(u["caio"]) and not m.FromCountry("BR").is_satisfied_by(u["caio"])
    assert m.HasTag("vip").is_satisfied_by(u["ana"]) and not m.HasTag("vip").is_satisfied_by(u["bia"])
    assert m.IsBanned().is_satisfied_by(u["caio"]) and not m.IsBanned().is_satisfied_by(u["ana"]) and not m.IsBanned().is_satisfied_by(u["edu"])
    assert m.Always().is_satisfied_by(u["ana"]) and not m.Never().is_satisfied_by(u["ana"])
    assert m.AgeAtLeast(18).describe() == "idade >= 18" and m.FromCountry("BR", "PT").describe() == "país em ('BR', 'PT')" and m.FromCountry("BR").describe() == "país em ('BR',)"
    assert m.HasTag("vip").describe() == "tem a tag 'vip'" and m.IsBanned().describe() == "está banido" and m.Always().describe() == "sempre" and m.Never().describe() == "nunca"


def test_leaf_validation(load_exercise):
    m = load_exercise("ex01_classic_specs")
    for bad in (-1, 1.5, True, "18"):
        with pytest.raises(ValueError, match="idade inválida"):
            m.AgeAtLeast(bad)
    with pytest.raises(ValueError, match="informe ao menos um país"):
        m.FromCountry()
    spec = m.AgeAtLeast(1)
    for call in (lambda: spec.and_("x"), lambda: spec.or_(3), lambda: spec.and_(None)):
        with pytest.raises(TypeError, match="esperava uma Specification"):
            call()
    with pytest.raises(TypeError):
        m.Specification()


def test_combinators_and_describe(load_exercise):
    m = load_exercise("ex01_classic_specs")
    u = users(m)
    adult, br, vip, banned = m.AgeAtLeast(18), m.FromCountry("BR"), m.HasTag("vip"), m.IsBanned()
    rule = adult.and_(br.or_(vip)).and_(banned.not_())
    assert rule.describe() == "((idade >= 18 E (país em ('BR',) OU tem a tag 'vip')) E NÃO está banido)"
    assert [x.name for x in u.values() if rule.is_satisfied_by(x)] == ["Ana", "Duda"]
    assert isinstance(adult.and_(br), m.AndSpec) and isinstance(adult.or_(br), m.OrSpec) and isinstance(adult.not_(), m.NotSpec)
    assert adult.not_().not_().is_satisfied_by(u["ana"]) is True and adult.not_().is_satisfied_by(u["bia"]) is True


def test_short_circuit(load_exercise):
    m = load_exercise("ex01_classic_specs")

    class Spy(m.Specification):
        def __init__(self, result):
            self.result, self.calls = result, 0

        def is_satisfied_by(self, candidate):
            self.calls += 1
            return self.result

        def describe(self):
            return f"spy {self.result}"

    ana = users(m)["ana"]
    false_, true_ = Spy(False), Spy(True)
    right = Spy(True)
    assert m.AndSpec(false_, right).is_satisfied_by(ana) is False and right.calls == 0
    assert m.AndSpec(true_, right).is_satisfied_by(ana) is True and right.calls == 1
    right2 = Spy(False)
    assert m.OrSpec(true_, right2).is_satisfied_by(ana) is True and right2.calls == 0
    assert m.OrSpec(false_, right2).is_satisfied_by(ana) is False and right2.calls == 1


def test_failures_explain_why_not(load_exercise):
    m = load_exercise("ex01_classic_specs")
    u = users(m)
    rule = m.AgeAtLeast(18).and_(m.FromCountry("BR", "PT").or_(m.HasTag("vip"))).and_(m.IsBanned().not_())
    assert rule.failures(u["ana"]) == [] and rule.failures(u["duda"]) == [] and rule.failures(u["edu"]) == []
    assert rule.failures(u["bia"]) == ["idade >= 18"]
    assert rule.failures(u["caio"]) == ["NÃO está banido"]
    assert rule.failures(u["ze"]) == ["idade >= 18", "país em ('BR', 'PT')", "tem a tag 'vip'", "NÃO está banido"]
    assert m.AgeAtLeast(40).failures(u["ana"]) == ["idade >= 40"] and m.AgeAtLeast(18).failures(u["ana"]) == []
    assert m.Never().failures(u["ana"]) == ["nunca"]


def test_all_of_any_of(load_exercise):
    m = load_exercise("ex01_classic_specs")
    u = users(m)
    a, b, c = m.AgeAtLeast(18), m.FromCountry("BR"), m.HasTag("vip")
    assert isinstance(m.all_of(), m.Always) and isinstance(m.any_of(), m.Never)
    assert m.all_of(a) is a and m.any_of(b) is b
    assert m.all_of(a, b, c).describe() == "((idade >= 18 E país em ('BR',)) E tem a tag 'vip')"
    assert m.any_of(a, b, c).describe() == "((idade >= 18 OU país em ('BR',)) OU tem a tag 'vip')"
    assert m.all_of(a, b, c).is_satisfied_by(u["ana"]) and not m.all_of(a, b, c).is_satisfied_by(u["duda"])
    assert m.any_of(b, c).is_satisfied_by(u["duda"]) and not m.any_of(b, c).is_satisfied_by(u["caio"])
    assert m.all_of().is_satisfied_by(u["ze"]) and not m.any_of().is_satisfied_by(u["ze"])


def test_filter_and_first_match(load_exercise):
    m = load_exercise("ex01_classic_specs")
    u = users(m)
    adult = m.AgeAtLeast(18)
    assert [x.name for x in m.filter_by(adult, u.values())] == ["Ana", "Caio", "Duda", "Edu"] and m.filter_by(m.Never(), u.values()) == []
    assert m.first_match(adult, u.values()).name == "Ana" and m.first_match(m.Never(), u.values()) is None and m.first_match(m.Never(), u.values(), "nada") == "nada"
    consumed = []

    def gen():
        for user in u.values():
            consumed.append(user.name)
            yield user

    assert m.first_match(m.HasTag("vip"), gen()).name == "Ana" and consumed == ["Ana"]


# ---------- ex02 ----------
def test_spec_basics(load_exercise):
    m = load_exercise("ex02_operator_specs")
    s = m.Spec(lambda x: x, "truthy")
    assert s("a") is True and s("") is False and s(0) is False and s([1]) is True
    assert m.Spec(len).description == "?" and repr(s) == "truthy"
    with pytest.raises(TypeError, match="fn precisa ser chamável"):
        m.Spec(3)
    assert m.Spec(lambda x: x > 1, "maior que 1").fn(2) is True


def test_operators_truth_table_and_descriptions(load_exercise):
    m = load_exercise("ex02_operator_specs")
    t, f = m.Spec(lambda x: True, "T"), m.Spec(lambda x: False, "F")
    assert [(a & b)(0) for a in (t, f) for b in (t, f)] == [True, False, False, False]
    assert [(a | b)(0) for a in (t, f) for b in (t, f)] == [True, True, True, False]
    assert (~t)(0) is False and (~f)(0) is True
    assert repr(t & f) == "(T e F)" and repr(t | f) == "(T ou F)" and repr(~t) == "não T" and repr(t & ~(f | t)) == "(T e não (F ou T))"
    assert isinstance(t & f, m.Spec) and isinstance(~t, m.Spec)


def test_short_circuit_and_new_objects(load_exercise):
    m = load_exercise("ex02_operator_specs")
    calls = []

    def probe(result):
        def fn(x):
            calls.append(result)
            return result
        return m.Spec(fn, str(result))

    assert (probe(False) & probe(True))(0) is False and calls == [False]
    calls.clear()
    assert (probe(True) | probe(False))(0) is True and calls == [True]
    calls.clear()
    assert (probe(True) & probe(True))(0) is True and calls == [True, True]
    a, b = m.Spec(lambda x: x > 0, "pos"), m.Spec(lambda x: x < 10, "pequeno")
    c = a & b
    assert c is not a and c is not b and a(5) is True and a(50) is True and b(-5) is True and b(50) is False and c(50) is False


def test_mixing_with_plain_functions(load_exercise):
    m = load_exercise("ex02_operator_specs")
    s = m.Spec(lambda x: x > 0, "positivo")

    def even(x):
        return x % 2 == 0

    assert (s & even)(4) is True and (s & even)(3) is False and repr(s & even) == "(positivo e even)"
    assert (even & s)(4) is True and (even | s)(-2) is True and repr(even & s) == "(even e positivo)"
    assert (s | (lambda x: x == -1))(-1) is True
    for call in (lambda: s & 3, lambda: 3 & s, lambda: s | "x", lambda: "x" | s):
        with pytest.raises(TypeError):
            call()


def test_spec_decorator_all_of_any_of(load_exercise):
    m = load_exercise("ex02_operator_specs")

    @m.spec("maior de idade")
    def adult(row):
        return row["age"] >= 18

    assert isinstance(adult, m.Spec) and repr(adult) == "maior de idade" and adult({"age": 20}) is True
    a, b, c = m.Spec(lambda x: x > 0, "a"), m.Spec(lambda x: x > 5, "b"), m.Spec(lambda x: x > 10, "c")
    assert repr(m.all_of(a, b, c)) == "((a e b) e c)" and repr(m.any_of(a, b, c)) == "((a ou b) ou c)"
    assert m.all_of(a, b, c)(11) is True and m.all_of(a, b, c)(7) is False and m.any_of(b, c)(7) is True and m.any_of(b, c)(1) is False
    assert m.all_of()(0) is True and repr(m.all_of()) == "sempre" and m.any_of()(0) is False and repr(m.any_of()) == "nunca"
    assert m.all_of(a) is a and isinstance(m.any_of(abs), m.Spec) and repr(m.any_of(abs)) == "abs"


def test_where(load_exercise):
    m = load_exercise("ex02_operator_specs")

    class Row:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    rule = m.where(country="BR", vip=True)
    assert rule({"country": "BR", "vip": True}) is True and rule({"country": "BR", "vip": False}) is False and rule({"country": "PT", "vip": True}) is False
    assert rule(Row(country="BR", vip=True)) is True and rule(Row(country="BR")) is False and rule({}) is False
    assert repr(rule) == "country == 'BR' e vip == True" == repr(m.where(country="BR", vip=True))
    assert m.where()({"anything": 1}) is True and repr(m.where()) == "sempre"
    assert m.where(x=None)({"x": None}) is True and m.where(x=None)({}) is False and m.where(n=0)({"n": 0}) is True and m.where(n=0)({"n": False}) is True
    combined = m.where(country="BR") & ~m.where(vip=True)
    assert combined({"country": "BR", "vip": False}) is True and combined({"country": "BR", "vip": True}) is False


def test_filter_by(load_exercise):
    m = load_exercise("ex02_operator_specs")
    rows = [{"n": i} for i in range(6)]
    assert m.filter_by(m.where(n=3), rows) == [{"n": 3}] and m.filter_by(lambda r: r["n"] % 2, rows) == [{"n": 1}, {"n": 3}, {"n": 5}]
    assert m.filter_by(m.all_of(), rows) == rows and m.filter_by(m.any_of(), rows) == []


# ---------- ex03 ----------
ROWS = [
    {"id": 1, "name": "Ana", "age": 30, "country": "BR", "vip": 0, "banned": 0},
    {"id": 2, "name": "Bia", "age": 17, "country": "BR", "vip": 1, "banned": 0},
    {"id": 3, "name": "Caio", "age": 45, "country": "PT", "vip": 0, "banned": 1},
    {"id": 4, "name": "Duda", "age": 22, "country": "US", "vip": 1, "banned": 0},
    {"id": 5, "name": "Edu", "age": 19, "country": "PT", "vip": 0, "banned": None},
    {"id": 6, "name": "Fabi", "age": 18, "country": "BR", "vip": 0, "banned": 0},
    {"id": 7, "name": "Gil", "age": None, "country": "BR", "vip": 1, "banned": 0},
    {"id": 8, "name": "Hana", "age": None, "country": None, "vip": None, "banned": None},
]


def test_field_construction_and_errors(load_exercise):
    m = load_exercise("ex03_field_dsl")
    assert isinstance(m.F.age, m.Field) and m.F.age.name == "age"
    for name in ("senha", "AGE", "age; DROP TABLE users"):
        with pytest.raises(AttributeError, match="coluna desconhecida"):
            m.Field(name)
    with pytest.raises(AttributeError, match="coluna desconhecida: senha"):
        m.F.senha
    with pytest.raises(TypeError):
        hash(m.F.age)
    for call in (lambda: m.F.age == None, lambda: m.F.age != None, lambda: m.F.age >= None):  # noqa: E711
        with pytest.raises(ValueError, match="use is_null"):
            call()
    with pytest.raises(ValueError, match="isin precisa de pelo menos um valor"):
        m.F.age.isin([])


def test_operators_build_specs_and_repr(load_exercise):
    m = load_exercise("ex03_field_dsl")
    F = m.F
    assert isinstance(F.age >= 18, m.Cmp) and isinstance((F.age >= 18) & (F.vip == 1), m.And) and isinstance((F.age >= 18) | (F.vip == 1), m.Or) and isinstance(~(F.age >= 18), m.Not)
    assert repr(F.age >= 18) == "age >= 18" and repr(F.country == "BR") == "country == 'BR'" and repr(F.banned != 1) == "banned != 1"
    assert repr((F.age >= 18) & ~(F.banned == 1)) == "(age >= 18 e não banned == 1)"
    assert repr(F.country.isin(["BR", "PT", "US"])) == "((country == 'BR' ou country == 'PT') ou country == 'US')"
    assert repr(F.age.between(18, 65)) == "(age >= 18 e age <= 65)" and repr(F.banned.is_null()) == "banned é nulo" and repr(F.banned.is_not_null()) == "não banned é nulo"


def test_three_valued_logic(load_exercise):
    m = load_exercise("ex03_field_dsl")
    F = m.F
    unknown_age = {"age": None, "vip": 0}
    assert (F.age >= 18).evaluate(unknown_age) is None and (F.age >= 18).evaluate({}) is None and (F.age >= 18).evaluate({"age": 20}) is True and (F.age >= 18).evaluate({"age": 3}) is False
    assert ((F.age >= 18) & (F.vip == 1)).evaluate(unknown_age) is False                  # falso E desconhecido = falso
    assert ((F.age >= 18) & (F.vip == 0)).evaluate(unknown_age) is None                   # verdadeiro E desconhecido = desconhecido
    assert ((F.age >= 18) | (F.vip == 0)).evaluate(unknown_age) is True                   # verdadeiro OU desconhecido = verdadeiro
    assert ((F.age >= 18) | (F.vip == 1)).evaluate(unknown_age) is None                   # falso OU desconhecido = desconhecido
    assert (~(F.age >= 18)).evaluate(unknown_age) is None and (~(F.age >= 18)).evaluate({"age": 3}) is True
    assert (F.age >= 18)(unknown_age) is False and (~(F.age >= 18))(unknown_age) is False  # desconhecido não satisfaz, nem mesmo a negação
    assert F.age.is_null().evaluate(unknown_age) is True and F.age.is_null().evaluate({"age": 1}) is False and F.age.is_null().evaluate({}) is True
    assert F.age.is_not_null()(unknown_age) is False and F.age.is_not_null()({"age": 1}) is True
    assert F.age.between(18, 65)({"age": 18}) is True and F.age.between(18, 65)({"age": 66}) is False and F.age.between(18, 65)(unknown_age) is False
    assert F.country.isin(["BR", "PT"])({"country": "PT"}) is True and F.country.isin(["BR"])({"country": "US"}) is False and F.country.isin(["BR"])({}) is False


def test_to_sql_text_and_params(load_exercise):
    m = load_exercise("ex03_field_dsl")
    F = m.F
    assert (F.age >= 18).to_sql() == ("age >= ?", (18,)) and (F.country == "BR").to_sql() == ("country = ?", ("BR",)) and (F.vip != 1).to_sql() == ("vip <> ?", (1,))
    assert (F.age <= 9).to_sql() == ("age <= ?", (9,)) and (F.age < 9).to_sql() == ("age < ?", (9,)) and (F.age > 9).to_sql() == ("age > ?", (9,))
    assert F.banned.is_null().to_sql() == ("banned IS NULL", ()) and F.banned.is_not_null().to_sql() == ("(NOT banned IS NULL)", ())
    assert (~(F.banned == 1)).to_sql() == ("(NOT banned = ?)", (1,))
    rule = (F.age >= 18) & (F.country.isin(["BR", "PT"]) | (F.vip == 1))
    assert rule.to_sql() == ("(age >= ? AND ((country = ? OR country = ?) OR vip = ?))", (18, "BR", "PT", 1))


def sql_ids(conn, spec):
    clause, params = spec.to_sql()
    return [row[0] for row in conn.execute(f"SELECT id FROM users WHERE {clause} ORDER BY id", params)]


def test_python_and_sql_agree_even_with_nulls(load_exercise):
    m = load_exercise("ex03_field_dsl")
    F = m.F
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, country TEXT, vip INTEGER, banned INTEGER)")
    conn.executemany("INSERT INTO users VALUES (:id, :name, :age, :country, :vip, :banned)", ROWS)
    specs = [
        F.age >= 18, F.age < 18, F.age == 30, F.age != 30, ~(F.age >= 18), ~(F.banned == 1), (F.banned == 0) | (F.vip == 1),
        ~((F.age >= 18) & (F.banned == 0)), ~((F.age >= 18) | (F.vip == 1)), F.country.isin(["US", "PT"]) & ~(F.vip == 1),
        F.banned.is_null(), F.banned.is_not_null() & (F.age >= 18), F.age.between(18, 30), ~F.age.between(18, 30), (F.age.is_null() | (F.age > 40)) & ~(F.country == "US"),
        (F.age >= 18) & (F.country.isin(["BR", "PT"]) | (F.vip == 1)) & ~(F.banned == 1),
    ]
    for spec in specs:
        assert [r["id"] for r in ROWS if spec(r)] == sql_ids(conn, spec), repr(spec)
    conn.close()


# ---------- ex04 ----------
def test_required(load_exercise):
    m = load_exercise("ex04_validator")
    r = m.required("name")
    assert r.error({"name": "Ana"}) is None and r.error({"name": 0}) is None and r.error({"name": False}) is None
    for item in ({}, {"name": None}, {"name": ""}, {"name": "   "}):
        assert r.error(item) == "name é obrigatório"


def test_min_value_and_max_len(load_exercise):
    m = load_exercise("ex04_validator")
    age = m.min_value("age", 18)
    assert age.error({"age": 18}) is None and age.error({"age": 17}) == "age deve ser >= 18" and age.error({}) is None and age.error({"age": None}) is None
    name = m.max_len("name", 3)
    assert name.error({"name": "Ana"}) is None and name.error({"name": "Ana Maria"}) == "name deve ter no máximo 3 caracteres" and name.error({}) is None and name.error({"name": None}) is None


def test_rule_when_and_callable_message(load_exercise):
    m = load_exercise("ex04_validator")
    rule = m.Rule(lambda i: i["age"] >= 18, lambda i: f"{i['name']} é menor de idade", when=lambda i: i.get("needs_adult"))
    assert rule.error({"name": "Bia", "age": 10}) is None                                   # a regra não se aplica
    assert rule.error({"name": "Bia", "age": 10, "needs_adult": True}) == "Bia é menor de idade"
    assert rule.error({"name": "Ana", "age": 30, "needs_adult": True}) is None
    plain = m.Rule(lambda i: False, "sempre falha")
    assert plain.error({}) == "sempre falha"
    with pytest.raises(KeyError):
        m.Rule(lambda i: i["x"] > 0, "m").error({})                                          # a exceção sobe


def test_validator_collects_all_errors(load_exercise):
    m = load_exercise("ex04_validator")
    v = m.Validator([m.required("name"), m.required("email"), m.min_value("age", 18), m.max_len("name", 5)])
    assert v.validate({"name": "Ana", "email": "a@b", "age": 30}) == [] and v.is_valid({"name": "Ana", "email": "a@b", "age": 30})
    assert v.validate({"name": "Ana Maria Silva", "age": 10}) == ["email é obrigatório", "age deve ser >= 18", "name deve ter no máximo 5 caracteres"]
    assert v.validate({}) == ["name é obrigatório", "email é obrigatório"] and not v.is_valid({})
    assert m.Validator().validate({"x": 1}) == [] and m.Validator().is_valid({})


def test_validator_add_chaining_first_error_and_ensure(load_exercise):
    m = load_exercise("ex04_validator")
    v = m.Validator()
    assert v.add(m.required("name")) is v
    assert v.add(m.required("email")).add(m.min_value("age", 18)) is v
    evaluated = []

    def spy(result, name):
        def check(item):
            evaluated.append(name)
            return result
        return m.Rule(check, name)

    ordered = m.Validator([spy(True, "a"), spy(False, "b"), spy(False, "c")])
    assert ordered.first_error({}) == "b" and evaluated == ["a", "b"]
    evaluated.clear()
    assert ordered.validate({}) == ["b", "c"] and evaluated == ["a", "b", "c"]
    assert m.Validator([spy(True, "x")]).first_error({}) is None
    ok = {"name": "Ana", "email": "a@b", "age": 30}
    assert v.ensure(ok) is ok
    with pytest.raises(m.ValidationError) as info:
        v.ensure({"age": 3})
    assert info.value.errors == ["name é obrigatório", "email é obrigatório", "age deve ser >= 18"]
    assert str(info.value) == "name é obrigatório; email é obrigatório; age deve ser >= 18"


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["specification_classico", "specification_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
