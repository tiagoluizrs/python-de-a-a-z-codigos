import pickle

import pytest


def test_parse_settings_ok(load_exercise):
    parse = load_exercise("ex01_config_errors").parse_settings
    lines = ["# comentário", "port = 8080", "", "  workers=4  "]
    assert parse(lines) == {"port": 8080, "workers": 4}


def test_parse_settings_invalid_value(load_exercise):
    module = load_exercise("ex01_config_errors")
    with pytest.raises(module.InvalidValueError) as info:
        module.parse_settings(["# c", "", "port = x"])
    error = info.value
    assert isinstance(error, module.ConfigError)
    assert (error.line_no, error.key, error.raw) == (3, "port", "x")
    assert str(error) == "linha 3: valor inválido para 'port': 'x'"
    assert isinstance(error.__cause__, ValueError)


def test_parse_settings_missing_separator(load_exercise):
    module = load_exercise("ex01_config_errors")
    with pytest.raises(module.MissingSeparatorError) as info:
        module.parse_settings(["a = 1", "abc"])
    assert str(info.value) == "linha 2: falta '=' em 'abc'"
    assert info.value.line_no == 2


def test_run_all(load_exercise):
    run_all = load_exercise("ex02_run_all").run_all
    assert run_all([lambda: 1, lambda: 2]) == [1, 2]
    calls = []

    def ok():
        calls.append("ok")
        return 1

    def bad_value():
        raise ValueError("v")

    def bad_type():
        raise TypeError("t")

    with pytest.raises(ExceptionGroup) as info:
        run_all([bad_value, ok, bad_type, ok])
    assert calls == ["ok", "ok"]            # todas rodaram
    assert info.value.message == "2 tarefas falharam"
    assert [type(e) for e in info.value.exceptions] == [ValueError, TypeError]


def test_count_by_type(load_exercise):
    count = load_exercise("ex02_run_all").count_by_type
    inner = ExceptionGroup("in", [KeyError("k"), ValueError("v")])
    outer = ExceptionGroup("out", [ValueError("a"), inner, ValueError("b")])
    assert count(outer) == {"ValueError": 3, "KeyError": 1}


def test_describe_chain(load_exercise):
    describe = load_exercise("ex03_chain").describe_chain
    try:
        try:
            try:
                int("x")
            except ValueError as error:
                raise KeyError("meio") from error
        except KeyError:
            raise RuntimeError("topo")          # contexto implícito
    except RuntimeError as final:
        chain = describe(final)
    assert [item.split(":")[0] for item in chain] == [
        "RuntimeError", "KeyError", "ValueError"]
    assert chain[-1] == "ValueError: invalid literal for int() with base 10: 'x'"


def test_describe_chain_suppressed(load_exercise):
    describe = load_exercise("ex03_chain").describe_chain
    try:
        try:
            {}["k"]
        except KeyError:
            raise ValueError("limpo") from None
    except ValueError as error:
        assert describe(error) == ["ValueError: limpo"]


def test_picklable_errors(load_exercise):
    module = load_exercise("ex04_picklable_error")
    error = module.ApiError(500, "falha")
    assert str(error) == "500: falha" and error.status == 500
    clone = pickle.loads(pickle.dumps(error))
    assert (type(clone), clone.status, clone.message, str(clone)) == (
        module.ApiError, 500, "falha", "500: falha")
    missing = module.NotFound("usuário 7")
    assert missing.status == 404 and isinstance(missing, module.ApiError)
    clone = pickle.loads(pickle.dumps(missing))
    assert type(clone) is module.NotFound
    assert (clone.status, clone.message) == (404, "usuário 7")
    assert str(clone) == "404: usuário 7"


def test_read_text_or_explain(load_exercise, tmp_path):
    module = load_exercise("ex05_errno_map")
    good = tmp_path / "ok.txt"
    good.write_text("olá", encoding="utf-8")
    assert module.read_text_or_explain(good) == "olá"

    with pytest.raises(module.ResourceMissing) as info:
        module.read_text_or_explain(tmp_path / "nao_existe.txt")
    assert isinstance(info.value, module.StorageError)
    assert isinstance(info.value.__cause__, FileNotFoundError)
    assert info.value.errno == info.value.__cause__.errno

    binary = tmp_path / "bin.dat"
    binary.write_bytes(b"\xff\xfe\x00")
    with pytest.raises(module.DecodeFailure) as info:
        module.read_text_or_explain(binary)
    assert isinstance(info.value.__cause__, UnicodeDecodeError)
