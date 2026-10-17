import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def sample(m):
    root = m.Directory("projeto")
    src = m.Directory("src")
    tests = m.Directory("tests")
    root.add(m.File("README.md", 120), src)
    src.add(m.File("util.py", 300), m.File("main.py", 800), tests)
    tests.add(m.File("test_main.py", 450))
    return root, src, tests


def test_tree_basics(load_exercise):
    m = load_exercise("ex01_fs_tree")
    root, src, tests = sample(m)
    assert root.size() == 1670 and src.size() == 1550 and root.count_files() == 4 and m.File("x", 5).size() == 5 and m.File("x", 5).count_files() == 1
    assert [c.name for c in root.children] == ["README.md", "src"] and [c.name for c in src.children] == ["main.py", "tests", "util.py"]
    assert [n.name for n in root.walk()] == ["projeto", "README.md", "src", "main.py", "tests", "test_main.py", "util.py"]
    assert tests.children[0].path == "/projeto/src/tests/test_main.py" and root.path == "/projeto" and m.File("solto", 1).path == "/solto"
    assert root.depth() == 4 and m.Directory("vazia").depth() == 1 and m.Directory("d").add(m.File("a", 1)).depth() == 2
    assert root.tree() == "projeto/ (1670)\n  README.md (120)\n  src/ (1550)\n    main.py (800)\n    tests/ (450)\n      test_main.py (450)\n    util.py (300)"


def test_find_and_remove(load_exercise):
    m = load_exercise("ex01_fs_tree")
    root, src, tests = sample(m)
    assert root.find(lambda n: n.name.endswith(".py")) == ["/projeto/src/main.py", "/projeto/src/tests/test_main.py", "/projeto/src/util.py"]
    assert root.find(lambda n: isinstance(n, m.Directory)) == ["/projeto", "/projeto/src", "/projeto/src/tests"]
    removed = src.remove("tests")
    assert removed is tests and removed.parent is None and root.size() == 1220 and root.count_files() == 3
    with pytest.raises(KeyError):
        src.remove("tests")
    assert root.children[1].children is not root.children[1].children                     # cópia a cada leitura
    root.children.clear()
    assert len(root.children) == 2


def test_tree_validation(load_exercise):
    m = load_exercise("ex01_fs_tree")
    for bad in ("", "a/b"):
        with pytest.raises(ValueError, match="nome inválido"):
            m.Directory(bad)
        with pytest.raises(ValueError, match="nome inválido"):
            m.File(bad, 1)
    with pytest.raises(ValueError, match="tamanho negativo"):
        m.File("a", -1)
    root, src, tests = sample(m)
    with pytest.raises(ValueError, match="já existe: src"):
        root.add(m.Directory("src"))
    with pytest.raises(ValueError, match="nó já tem pai"):
        m.Directory("outra").add(src)
    with pytest.raises(ValueError, match="ciclo"):
        tests.add(root)
    with pytest.raises(ValueError, match="ciclo"):
        root.add(root)
    d = m.Directory("d")
    assert d.add(m.File("a", 1), m.File("b", 2)) is d and d.size() == 3
    with pytest.raises(ValueError, match="já existe: a"):
        d.add(m.File("c", 1), m.File("a", 5))
    assert d.size() == 4                                                                      # o "c" da mesma chamada já entrou


def test_tree_is_iterative(load_exercise):
    m = load_exercise("ex01_fs_tree")
    top = m.Directory("n0")
    cur = top
    for i in range(1, 5000):
        nxt = m.Directory(f"n{i}")
        cur.add(nxt)
        cur = nxt
    cur.add(m.File("fim", 7))
    assert top.size() == 7 and top.count_files() == 1 and top.depth() == 5001
    assert len(list(top.walk())) == 5001 and cur.children[0].path.count("/") == 5001
    assert len(top.tree().splitlines()) == 5001 and top.find(lambda n: n.name == "fim")[0].endswith("/n4999/fim")


# ---------- ex02 ----------
def deep_list(n):
    data = "folha"
    for _ in range(n):
        data = [data]
    return data


def test_depth_and_count_nodes(load_exercise):
    m = load_exercise("ex02_json_walk")
    assert m.depth(5) == 0 and m.depth([]) == 1 and m.depth({}) == 1 and m.depth([1, 2]) == 1
    assert m.depth({"a": [1, {"b": []}]}) == 4
    assert m.count_nodes(5) == 1 and m.count_nodes([]) == 1 and m.count_nodes({"a": [1, 2], "b": 3}) == 5
    huge = deep_list(100_000)
    assert m.depth(huge) == 100_000 and m.count_nodes(huge) == 100_001


def test_flatten(load_exercise):
    m = load_exercise("ex02_json_walk")
    data = {"a": 1, "b": {"c": [10, 20, {"d": None}], "e": {}}, "f": []}
    flat = m.flatten(data)
    assert flat == {("a",): 1, ("b", "c", 0): 10, ("b", "c", 1): 20, ("b", "c", 2, "d"): None, ("b", "e"): {}, ("f",): []}
    assert list(flat) == [("a",), ("b", "c", 0), ("b", "c", 1), ("b", "c", 2, "d"), ("b", "e"), ("f",)]
    assert m.flatten(7) == {(): 7} and m.flatten([]) == {(): []}
    assert len(m.flatten(deep_list(3000))) == 1


def test_unflatten_roundtrip_and_errors(load_exercise):
    m = load_exercise("ex02_json_walk")
    data = {"a": 1, "b": {"c": [10, 20, {"d": None}], "e": {}}, "f": [], "g": [[1, 2], [3]]}
    assert m.unflatten(m.flatten(data)) == data
    assert m.unflatten({(): 5}) == 5
    with pytest.raises(ValueError, match="índices não consecutivos em x"):
        m.unflatten({("x", 0): 1, ("x", 2): 3})
    with pytest.raises(ValueError, match="índices não consecutivos em raiz"):
        m.unflatten({(1,): "a"})
    with pytest.raises(ValueError, match="chaves misturadas em raiz"):
        m.unflatten({(0,): 1, ("a",): 2})
    with pytest.raises(ValueError):
        m.unflatten({(): 1, ("a",): 2})


def test_find_paths(load_exercise):
    m = load_exercise("ex02_json_walk")
    data = {"a": 1, "b": [2, {"c": 3}, 4], "d": "x"}
    assert m.find_paths(data, lambda v: isinstance(v, int) and v >= 3) == [("b", 1, "c"), ("b", 2)]
    assert m.find_paths(data, lambda v: False) == []


# ---------- ex03 ----------
def test_expression_eval_vars_str(load_exercise):
    m = load_exercise("ex03_expression")
    e = m.Mul(m.Add(m.Var("x"), m.Num(2)), m.Neg(m.Var("y")))
    assert e.evaluate({"x": 3, "y": 4}) == -20 and e.variables() == {"x", "y"}
    assert str(e) == "(x + 2) * -y"
    assert str(m.Add(m.Num(1), m.Mul(m.Num(2), m.Num(3)))) == "1 + 2 * 3"
    assert str(m.Add(m.Num(1), m.Add(m.Num(2), m.Num(3)))) == "1 + (2 + 3)" and str(m.Add(m.Add(m.Num(1), m.Num(2)), m.Num(3))) == "1 + 2 + 3"
    assert str(m.Neg(m.Add(m.Var("a"), m.Var("b")))) == "-(a + b)" and str(m.Neg(m.Neg(m.Var("a")))) == "--a"
    assert str(m.Mul(m.Num(2.5), m.Num(-4))) == "2.5 * -4" and str(m.Mul(m.Mul(m.Var("a"), m.Var("b")), m.Var("c"))) == "a * b * c"
    with pytest.raises(NameError, match="variável indefinida: z"):
        m.Add(m.Var("x"), m.Var("z")).evaluate({"x": 1})
    assert m.Num(3).variables() == set() and m.Num(3).evaluate({}) == 3


def test_expression_simplify(load_exercise):
    m = load_exercise("ex03_expression")
    x, y = m.Var("x"), m.Var("y")
    n = m.Num
    assert m.Add(n(2), n(3)).simplify() == n(5) and m.Mul(n(2), n(4)).simplify() == n(8)
    assert m.Add(n(0), x).simplify() == x and m.Add(x, n(0)).simplify() == x
    assert m.Mul(n(1), x).simplify() == x and m.Mul(x, n(1)).simplify() == x
    assert m.Mul(n(0), x).simplify() == n(0) and m.Mul(x, n(0)).simplify() == n(0)
    assert m.Neg(n(4)).simplify() == n(-4) and m.Neg(m.Neg(x)).simplify() == x
    assert m.Add(m.Mul(x, n(1)), m.Mul(n(0), y)).simplify() == x
    assert m.Add(m.Add(n(1), n(2)), m.Mul(x, m.Add(n(0), n(1)))).simplify() == m.Add(n(3), x)
    assert m.Mul(m.Add(x, n(0)), m.Neg(m.Neg(y))).simplify() == m.Mul(x, y)
    expr = m.Add(m.Mul(n(2), m.Add(x, n(0))), m.Neg(m.Neg(n(3))))
    assert expr.simplify().evaluate({"x": 5}) == expr.evaluate({"x": 5}) and str(expr.simplify()) == "2 * x + 3"
    assert x.simplify() is x and n(3).simplify() == n(3)


def test_expression_equality_and_hash(load_exercise):
    m = load_exercise("ex03_expression")
    assert m.Add(m.Num(1), m.Var("x")) == m.Add(m.Num(1), m.Var("x")) and m.Add(m.Num(1), m.Var("x")) != m.Add(m.Var("x"), m.Num(1))
    assert len({m.Num(1), m.Num(1), m.Var("a")}) == 2


# ---------- ex04 ----------
def registry(m):
    r = m.RoleRegistry()
    r.define("viewer", ["read"])
    r.define("editor", ["write"], includes=["viewer"])
    r.define("auditor", ["audit", "read"])
    r.define("admin", ["delete"], includes=["editor", "auditor"])
    return r


def test_permissions_and_queries(load_exercise):
    m = load_exercise("ex04_permissions")
    r = registry(m)
    assert r.permissions("viewer") == ["read"] and r.permissions("editor") == ["read", "write"]
    assert r.permissions("admin") == ["audit", "delete", "read", "write"]
    assert r.can("editor", "read") and not r.can("editor", "audit") and r.can("admin", "write")
    assert r.roles_with("read") == ["admin", "auditor", "editor", "viewer"] and r.roles_with("audit") == ["admin", "auditor"] and r.roles_with("nope") == []
    assert r.explain("admin", "write") == ["admin", "editor"] and r.explain("admin", "delete") == ["admin"]
    assert r.explain("admin", "read") == ["admin", "auditor"]                                  # 'auditor' < 'editor': o caminho mais curto, alfabético
    assert r.explain("editor", "audit") is None and r.explain("viewer", "read") == ["viewer"]
    with pytest.raises(KeyError):
        r.permissions("ghost")
    with pytest.raises(KeyError):
        r.explain("ghost", "read")


def test_diamond_visited_once(load_exercise):
    m = load_exercise("ex04_permissions")
    r = m.RoleRegistry()
    r.define("base", ["x"])
    r.define("left", ["l"], includes=["base"])
    r.define("right", ["r"], includes=["base"])
    r.define("top", [], includes=["left", "right"])
    assert r.permissions("top") == ["l", "r", "x"] and r.explain("top", "x") == ["top", "left", "base"]


def test_define_errors_and_cycles(load_exercise):
    m = load_exercise("ex04_permissions")
    r = registry(m)
    with pytest.raises(ValueError, match="role já existe: viewer"):
        r.define("viewer")
    with pytest.raises(ValueError, match="role desconhecida: ghost"):
        r.define("x", includes=["viewer", "ghost", "other"])
    assert "x" not in r.roles_with("read")
    with pytest.raises(ValueError, match="ciclo: viewer -> admin -> editor -> viewer"):
        r.include("viewer", "admin")
    with pytest.raises(ValueError, match="ciclo: viewer -> viewer"):
        r.include("viewer", "viewer")
    with pytest.raises(KeyError):
        r.include("viewer", "ghost")
    with pytest.raises(KeyError):
        r.include("ghost", "viewer")
    r.include("viewer", "auditor")                                                              # sem ciclo: permitido
    assert r.permissions("viewer") == ["audit", "read"]
    r.include("viewer", "auditor")                                                              # repetido: sem efeito
    assert r.explain("viewer", "audit") == ["viewer", "auditor"]


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["composite_classico", "composite_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
