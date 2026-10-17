import io
import json
from pathlib import Path

import pytest

import todo_argparse
import todo_click
import todo_core as core
import todo_typer


# ---------- os três front-ends de exemplo, contra o mesmo núcleo ----------
@pytest.fixture
def store(tmp_path):
    return tmp_path / "t.json"


def argparse_cli(store, *args):
    out, err = io.StringIO(), io.StringIO()
    import contextlib
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = todo_argparse.main(["-f", str(store), *args])
    return code, out.getvalue(), err.getvalue()


def click_cli(store, *args, input=None):
    from click.testing import CliRunner
    result = CliRunner().invoke(todo_click.cli, ["-f", str(store), *args], input=input)
    return result.exit_code, result.output


def typer_cli(store, *args, input=None):
    from typer.testing import CliRunner
    result = CliRunner().invoke(todo_typer.app, list(args), env={"TODO_FILE": str(store)}, input=input)
    return result.exit_code, result.output


@pytest.mark.parametrize("name", ["argparse", "click", "typer"])
def test_three_frontends_same_behavior(name, store):
    def run(*args, input=None):
        if name == "argparse":
            code, out, _ = argparse_cli(store, *args)
            return code, out
        return (click_cli if name == "click" else typer_cli)(store, *args, input=input)

    assert run("add", "Comprar café", "-t", "casa", "-t", "urgente", "--due", "2026-11-01") == (0, "tarefa 1 criada\n")
    assert run("add", "Estudar") == (0, "tarefa 2 criada\n")
    assert run("done", "1") == (0, "tarefa 1 concluída\n")
    assert run("list", "--status", "open") == (0, "[ ]   2  Estudar\n")
    code, out = run("list", "--json")
    assert code == 0 and [t["text"] for t in json.loads(out)] == ["Comprar café", "Estudar"]
    assert run("rm", "2", "--dry-run") == (0, "(simulação) removeria a tarefa 2\n")
    assert [t.id for t in core.load(store)] == [1, 2]


def test_business_errors_go_to_stderr_with_code_1(store):
    code, out, err = argparse_cli(store, "done", "99")
    assert (code, out, err) == (1, "", "todo: erro: tarefa 99 não existe\n")
    code, out, err = argparse_cli(store, "add", "x", "--due", "ontem")
    assert code == 1 and "AAAA-MM-DD" in err
    assert click_cli(store, "done", "99")[0] == 1 and typer_cli(store, "done", "99")[0] == 1


def test_usage_errors_exit_2(store):
    with pytest.raises(SystemExit) as info:
        argparse_cli(store, "list", "--status", "talvez")
    assert info.value.code == 2
    assert click_cli(store, "list", "--status", "talvez")[0] == 2 and typer_cli(store, "list", "--status", "talvez")[0] == 2


def test_confirmation_and_atomic_save(store):
    core.add(store, "x")
    code, out = click_cli(store, "rm", "1", input="n\n")
    assert code == 1 and len(core.load(store)) == 1                       # respondeu não: nada mudou
    code, out = click_cli(store, "rm", "1", input="y\n")
    assert code == 0 and core.load(store) == [] and not list(store.parent.glob("*.tmp"))


def test_file_precedence(monkeypatch, tmp_path):
    monkeypatch.delenv("TODO_FILE", raising=False)
    assert core.resolve_path(None) == core.DEFAULT_FILE
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "env.json"))
    assert core.resolve_path(None) == tmp_path / "env.json"
    assert core.resolve_path(tmp_path / "flag.json") == tmp_path / "flag.json"


def test_corrupted_file_is_a_clean_error(store):
    store.write_text("{isso não é json", encoding="utf-8")
    code, out, err = argparse_cli(store, "list")
    assert code == 1 and "corrompido" in err and "Traceback" not in err


# ---------- ex01 ----------
def wc(load_exercise, argv, stdin=b"", tmp=None):
    m = load_exercise("ex01_wc")
    out, err = io.StringIO(), io.StringIO()
    code = m.main(argv, stdin=io.BytesIO(stdin), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def test_wc_files_and_total(load_exercise, tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_bytes(b"um dois\ntres\n")
    b.write_bytes(b"x\n")
    code, out, err = wc(load_exercise, [str(a), str(b)])
    assert code == 0 and err == ""
    assert out.splitlines() == [f"      2       3      13 {a}", f"      1       1       2 {b}", "      3       4      15 total"]


def test_wc_flags_and_stdin(load_exercise):
    code, out, _ = wc(load_exercise, ["-l"], stdin=b"a\nb\nc\n")
    assert (code, out) == (0, "      3\n")
    code, out, _ = wc(load_exercise, ["-c", "-l", "-"], stdin=b"a b\n")
    assert out == "      1       4\n"                                    # ordem fixa: linhas, depois bytes
    assert wc(load_exercise, [], stdin=b"x y z\n")[1] == "      1       3       6\n"


def test_wc_missing_file_keeps_going(load_exercise, tmp_path):
    a = tmp_path / "a.txt"
    a.write_bytes(b"oi\n")
    code, out, err = wc(load_exercise, ["nada.txt", str(a)])
    assert code == 1 and "wc: nada.txt: arquivo ou diretório inexistente" in err
    assert out == f"      1       1       3 {a}\n"                      # só um arquivo lido: não há linha 'total'


def test_wc_usage_error(load_exercise):
    with pytest.raises(SystemExit) as info:
        wc(load_exercise, ["--bogus"])
    assert info.value.code == 2


# ---------- ex02 ----------
def test_resolve_precedence(load_exercise):
    m = load_exercise("ex02_config")
    defaults, file_values, env = {"port": 8000}, {"port": 9000}, {"APP_PORT": "9100"}
    assert m.resolve("port", {"port": 7000}, env, file_values, defaults, int) == (7000, "flag")
    assert m.resolve("port", {"port": None}, env, file_values, defaults, int) == (9100, "env")
    assert m.resolve("port", {}, {}, file_values, defaults, int) == (9000, "arquivo")
    assert m.resolve("port", {}, {}, {}, defaults, int) == (8000, "padrão")


def test_resolve_conversion_and_errors(load_exercise):
    m = load_exercise("ex02_config")
    assert m.resolve("debug", {}, {"APP_DEBUG": "1"}, {}, {}, lambda s: s == "1") == (True, "env")
    assert m.resolve("port", {"port": 0}, {"APP_PORT": "x"}, {}, {}, int) == (0, "flag")        # 0 é um valor, não 'ausente'
    with pytest.raises(ValueError, match=r"APP_PORT: valor inválido 'abc'"):
        m.resolve("port", {}, {"APP_PORT": "abc"}, {}, {"port": 1}, int)
    with pytest.raises(KeyError):
        m.resolve("host", {}, {}, {}, {})
    assert m.resolve("mode", {}, {"X_MODE": "fast"}, {}, {}, prefix="X_") == ("fast", "env")


def test_resolve_all(load_exercise):
    m = load_exercise("ex02_config")
    values, origins = m.resolve_all(["host", "port", "debug"], {"host": "h"}, {"APP_PORT": "81"}, {}, {"debug": False, "host": "x", "port": 1},
                                    {"port": int})
    assert values == {"host": "h", "port": 81, "debug": False} and list(values) == ["host", "port", "debug"]
    assert origins == {"host": "flag", "port": "env", "debug": "padrão"}


# ---------- ex03 ----------
def test_run_codes(load_exercise):
    m = load_exercise("ex03_exit_codes")
    err = io.StringIO()
    assert m.run(lambda argv: 7, [], err) == 7 and m.run(lambda argv: None, [], err) == 0 and err.getvalue() == ""
    assert m.run(lambda argv: (_ for _ in ()).throw(m.UserError("faltou o arquivo")), [], err) == 1
    assert err.getvalue() == "erro: faltou o arquivo\n"


def test_run_signals_and_pipes(load_exercise):
    m = load_exercise("ex03_exit_codes")

    def raising(exc):
        def main(argv):
            raise exc
        return main

    err = io.StringIO()
    assert m.run(raising(KeyboardInterrupt()), [], err) == 130 and err.getvalue() == "\n"
    err = io.StringIO()
    assert m.run(raising(BrokenPipeError()), [], err) == 0 and err.getvalue() == ""
    assert m.run(raising(SystemExit(2)), [], io.StringIO()) == 2 and m.run(raising(SystemExit()), [], io.StringIO()) == 0
    err = io.StringIO()
    assert m.run(raising(SystemExit("mensagem")), [], err) == 1 and err.getvalue() == "mensagem\n"


def test_run_unexpected_errors(load_exercise):
    m = load_exercise("ex03_exit_codes")

    def bug(argv):
        return {}["x"]

    err = io.StringIO()
    assert m.run(bug, [], err) == 70
    assert err.getvalue() == "erro interno: KeyError: 'x'\n" and "Traceback" not in err.getvalue()
    err = io.StringIO()
    assert m.run(bug, [], err, debug=True) == 70
    assert "Traceback" in err.getvalue() and err.getvalue().rstrip().endswith("erro interno: KeyError: 'x'")


def test_run_passes_argv(load_exercise):
    m = load_exercise("ex03_exit_codes")
    seen = []
    m.run(lambda argv: seen.append(argv), ["a", "b"], io.StringIO())
    assert seen == [["a", "b"]]


# ---------- ex04 ----------
@pytest.fixture
def csv_file(tmp_path):
    path = tmp_path / "notas.csv"
    path.write_text("nome,nota\nana,1\nbia,3\ncau,2\n", encoding="utf-8")
    return path


def test_click_stats_text_and_json(load_exercise, csv_file):
    from click.testing import CliRunner
    m = load_exercise("ex04_click_stats")
    result = CliRunner().invoke(m.stats, [str(csv_file), "-c", "nota"])
    assert result.exit_code == 0 and result.output.splitlines() == ["n=3", "min=1.0", "max=3.0", "mean=2.0"]
    result = CliRunner().invoke(m.stats, [str(csv_file), "--column", "nota", "--format", "json"])
    assert json.loads(result.output) == {"n": 3, "min": 1.0, "max": 3.0, "mean": 2.0} and result.output.count("\n") == 1


def test_click_stats_errors(load_exercise, csv_file, tmp_path):
    from click.testing import CliRunner
    m = load_exercise("ex04_click_stats")
    runner = CliRunner()
    missing = runner.invoke(m.stats, [str(tmp_path / "nao.csv"), "-c", "x"])
    assert missing.exit_code == 2                                          # Path(exists=True) é erro de uso
    bad_col = runner.invoke(m.stats, [str(csv_file), "-c", "idade"])
    assert bad_col.exit_code == 1 and "coluna 'idade' não existe (colunas: nome, nota)" in bad_col.output
    assert runner.invoke(m.stats, [str(csv_file), "-c", "nota", "--format", "xml"]).exit_code == 2
    assert runner.invoke(m.stats, [str(csv_file)]).exit_code == 2           # --column é obrigatória


def test_click_stats_invalid_values(load_exercise, tmp_path):
    from click.testing import CliRunner
    m = load_exercise("ex04_click_stats")
    path = tmp_path / "sujo.csv"
    path.write_text("nota\n1\nabc\n3\n", encoding="utf-8")
    strict = CliRunner().invoke(m.stats, [str(path), "-c", "nota"])
    assert strict.exit_code == 1 and "linha 3: valor inválido 'abc'" in strict.output
    lenient = CliRunner().invoke(m.stats, [str(path), "-c", "nota", "--skip-invalid"])
    assert lenient.exit_code == 0 and "n=2" in lenient.output and "mean=2.0" in lenient.output
    empty = tmp_path / "vazio.csv"
    empty.write_text("nota\nx\n", encoding="utf-8")
    result = CliRunner().invoke(m.stats, [str(empty), "-c", "nota", "--skip-invalid"])
    assert result.exit_code == 1 and "nenhum valor numérico" in result.output


# ---------- ex05 ----------
ROWS = [{"nome": "Ana", "nota": 9.5}, {"nome": "Bia, a", "nota": 7}]


def test_render_machine_formats(load_exercise):
    m = load_exercise("ex05_render")
    assert json.loads(m.render(ROWS, "json")) == ROWS and "\n" not in m.render(ROWS, "json")
    assert m.render(ROWS, "csv") == 'nome,nota\nAna,9.5\n"Bia, a",7'
    assert m.render(ROWS, "plain") == "Ana\t9.5\nBia, a\t7"
    assert m.render([], "csv") == "" and m.render([], "plain") == "" and m.render([], "json") == "[]"


def test_render_table_color_and_empty(load_exercise):
    m = load_exercise("ex05_render")
    plain = m.render(ROWS, "table", color=False)
    assert "\x1b" not in plain and "nome" in plain and "Bia, a" in plain and not plain.endswith("\n")
    assert max(len(line) for line in plain.splitlines()) <= 80
    assert "\x1b" in m.render(ROWS, "table", color=True)
    assert m.render([], "table") == "(vazio)"
    narrow = m.render([{"x": "palavra " * 10}], "table", width=30)
    assert max(len(line) for line in narrow.splitlines()) <= 30
    with pytest.raises(ValueError, match="formato desconhecido: 'xml'"):
        m.render(ROWS, "xml")


def test_want_color(load_exercise):
    m = load_exercise("ex05_render")
    assert m.want_color("always", False, {"NO_COLOR": "1"}) is True and m.want_color("never", True, {}) is False
    assert m.want_color("auto", True, {}) is True and m.want_color("auto", False, {}) is False
    assert m.want_color("auto", True, {"NO_COLOR": ""}) is False
    with pytest.raises(ValueError):
        m.want_color("talvez", True, {})


# ---------- ex06 ----------
def test_typer_resize(load_exercise):
    from typer.testing import CliRunner
    m = load_exercise("ex06_typer_app")
    runner = CliRunner()
    result = runner.invoke(m.app, ["resize", "1.5", "2.4", "-s", "2"])
    assert result.exit_code == 0 and result.output.split() == ["3", "5"]
    result = runner.invoke(m.app, ["resize", "2.7", "--mode", "floor", "-v"])
    assert result.output.splitlines() == ["escala=1.0 modo=floor", "2"]
    assert runner.invoke(m.app, ["resize", "1", "--scale", "-1"]).exit_code == 2
    assert runner.invoke(m.app, ["resize", "1", "--mode", "ceil"]).exit_code == 2
    assert runner.invoke(m.app, ["resize"]).exit_code == 2                  # falta o argumento
    assert runner.invoke(m.app, ["resize", "abc"]).exit_code == 2           # não é float
    assert runner.invoke(m.app, ["reset"]).output.strip() == "zerado"
