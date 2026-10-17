import copy
import pickle

import pytest


@pytest.mark.parametrize("text, expected", [("1", True), ("TRUE", True), (" yes ", True), ("On", True), ("0", False), ("false", False),
                                            ("No", False), ("off", False), ("", False)])
def test_as_bool(load_exercise, text, expected):
    assert load_exercise("ex01_env_parsing").as_bool(text) is expected


def test_as_bool_invalid(load_exercise):
    with pytest.raises(ValueError, match="^DEBUG: booleano inválido"):
        load_exercise("ex01_env_parsing").as_bool("talvez", name="DEBUG")


def test_as_int(load_exercise):
    m = load_exercise("ex01_env_parsing")
    assert m.as_int(" 8080 ") == 8080 and m.as_int("-5") == -5 and m.as_int("5", minimum=5, maximum=5) == 5
    for text, kwargs in (("abc", {}), ("True", {}), ("1.5", {}), ("", {}), ("0", {"minimum": 1}), ("70000", {"maximum": 65535})):
        with pytest.raises(ValueError, match="^PORT: "):
            m.as_int(text, name="PORT", **kwargs)


def test_as_list(load_exercise):
    as_list = load_exercise("ex01_env_parsing").as_list
    assert as_list("a, b ,c") == ["a", "b", "c"] and as_list("") == [] and as_list(" , ,") == [] and as_list("1;2;3", ";", int) == [1, 2, 3]
    with pytest.raises(ValueError):
        as_list("1,x", cast=int)


@pytest.mark.parametrize("text, seconds", [("90", 90), ("30s", 30), ("5m", 300), ("2h", 7200), ("1d", 86400), ("1.5h", 5400), ("500ms", 0.5), ("5 m", 300)])
def test_as_duration(load_exercise, text, seconds):
    value = load_exercise("ex01_env_parsing").as_duration(text)
    assert value == pytest.approx(seconds) and isinstance(value, float)


@pytest.mark.parametrize("text", ["", "abc", "-5s", "5x", "1h30m", "5.s"])
def test_as_duration_invalid(load_exercise, text):
    with pytest.raises(ValueError, match="^TIMEOUT: "):
        load_exercise("ex01_env_parsing").as_duration(text, name="TIMEOUT")


DEFAULTS = {"host": "localhost", "port": 8000, "debug": False, "ratio": 0.5, "tags": ["a"], "db_url": "sqlite://"}


def test_layers_precedence_and_sources(load_exercise):
    load = load_exercise("ex02_layered").load_settings
    settings, sources = load(DEFAULTS, file_data={"host": "0.0.0.0", "port": 9000}, environ={"APP_PORT": "9100", "APP_DEBUG": "yes", "OTHER": "x"},
                             cli={"port": 9200, "host": None})
    assert settings == {"host": "0.0.0.0", "port": 9200, "debug": True, "ratio": 0.5, "tags": ["a"], "db_url": "sqlite://"}
    assert sources == {"host": "file", "port": "cli", "debug": "env", "ratio": "default", "tags": "default", "db_url": "default"}
    assert DEFAULTS["port"] == 8000                                  # não altera os padrões


def test_layers_env_conversion(load_exercise):
    load = load_exercise("ex02_layered").load_settings
    env = {"APP_DB_URL": "postgres://x", "APP_RATIO": "0.75", "APP_TAGS": "x, y ,z", "APP_DEBUG": "0", "APP_UNKNOWN": "1", "PORT": "1"}
    settings, sources = load(DEFAULTS, environ=env)
    assert settings["db_url"] == "postgres://x" and settings["ratio"] == 0.75 and settings["tags"] == ["x", "y", "z"] and settings["debug"] is False
    assert sources["db_url"] == "env" and sources["port"] == "default"
    assert load(DEFAULTS, environ={"X_PORT": "1"}, prefix="X_")[0]["port"] == 1


def test_layers_errors(load_exercise):
    load = load_exercise("ex02_layered").load_settings
    with pytest.raises(ValueError, match="APP_PORT"):
        load(DEFAULTS, environ={"APP_PORT": "abc"})
    with pytest.raises(ValueError, match="APP_DEBUG"):
        load(DEFAULTS, environ={"APP_DEBUG": "talvez"})
    with pytest.raises(KeyError):
        load(DEFAULTS, file_data={"nope": 1})
    with pytest.raises(KeyError):
        load(DEFAULTS, cli={"nope": 1})


def test_secret_masks_everywhere(load_exercise):
    Secret = load_exercise("ex03_secret").Secret
    s = Secret("senha-longa-123")
    assert repr(s) == str(s) == "Secret('**********')" and "senha" not in f"{s!r} {s} {[s]} {{'k': {s!r}}}"
    assert s.reveal() == "senha-longa-123" and Secret("a") .__repr__() == repr(s)
    assert bool(Secret("x")) is True and bool(Secret("")) is False
    assert not hasattr(s, "__dict__") and "senha" not in repr(getattr(s, "__slots__", ""))


def test_secret_equality_hash_and_serialization(load_exercise):
    Secret = load_exercise("ex03_secret").Secret
    assert Secret("abc") == Secret("abc") and Secret("abc") != Secret("abd") and (Secret("abc") == "abc") is False
    with pytest.raises(TypeError):
        hash(Secret("abc"))
    with pytest.raises(TypeError):
        pickle.dumps(Secret("abc"))
    with pytest.raises(TypeError):
        copy.copy(Secret("abc"))
    with pytest.raises(TypeError):
        len(Secret("abc"))


def test_dotenv_basic(load_exercise):
    parse = load_exercise("ex04_dotenv").parse_dotenv
    text = """
# comentário
A=1
  B = valor com espaços
export C=3
D="x y"
E='raw \\n'
F=
G=sem aspas # comentário
H="com # hash"
"""
    assert parse(text) == {"A": "1", "B": "valor com espaços", "C": "3", "D": "x y", "E": "raw \\n", "F": "", "G": "sem aspas", "H": "com # hash"}


def test_dotenv_escapes_and_expansion(load_exercise):
    parse = load_exercise("ex04_dotenv").parse_dotenv
    assert parse('A="l1\\nl2"\nB="diz \\"oi\\""') == {"A": "l1\nl2", "B": 'diz "oi"'}
    text = "BASE=/srv\nPATH_X=${BASE}/app\nQ='${BASE}'\nD=\"${BASE}/d\"\nE=${HOME_X}/e\nF=${NOPE}x"
    assert parse(text, environ={"HOME_X": "/home"}) == {"BASE": "/srv", "PATH_X": "/srv/app", "Q": "${BASE}", "D": "/srv/d", "E": "/home/e", "F": "x"}


@pytest.mark.parametrize("text, line", [("A=1\nSEMIGUAL\n", 2), ("1A=x", 1), ("A=1\n\n-X=2", 3), ("=x", 1)])
def test_dotenv_errors(load_exercise, text, line):
    with pytest.raises(ValueError, match=f"linha {line}"):
        load_exercise("ex04_dotenv").parse_dotenv(text)


def test_mask_and_scan(load_exercise):
    m = load_exercise("ex05_secret_scanner")
    assert m.mask("abcdefgh") == "ab****gh" and m.mask("abc") == "***" and m.mask("") == "" and m.mask("1234567") == "*******"
    text = """\
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
password = "hunter2hunter2"
api_key = os.environ["API_KEY"]
token = "changeme"
-----BEGIN RSA PRIVATE KEY-----
jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dBjftJeZ4CVPmB92K27uhbUJU1p1r_wW1gFWFOEjXk"
normal = "texto qualquer sem segredo"
SECRET: 'curto'
Api-Key = 'Xx9Zz8Yy7Ww6'
"""
    findings = m.scan_text(text)
    assert [(f["line"], f["kind"]) for f in findings] == [(1, "aws-access-key"), (2, "assignment"), (5, "private-key"), (6, "jwt"), (9, "assignment")]
    assert findings[1]["match"] == "hu" + "*" * 10 + "r2" and findings[0]["match"].startswith("AK") and findings[0]["match"].endswith("LE")
    assert m.scan_text("") == [] and m.scan_text('password = "your-password-here"\nsecret = "<segredo>"\ntoken = "${TOKEN}"\nkey = "example-key-123"') == []


def test_validate_settings_ok(load_exercise):
    m = load_exercise("ex06_settings_validation")
    schema = {"port": {"type": int, "min": 1, "max": 65535, "default": 8000}, "mode": {"type": str, "choices": ["dev", "prod"], "required": True},
              "debug": {"type": bool, "default": False}, "ratio": {"type": float}}
    assert m.validate_settings({"mode": "dev", "ratio": 1}, schema) == {"port": 8000, "mode": "dev", "debug": False, "ratio": 1}
    assert m.validate_settings({"mode": "prod", "port": 1, "debug": True}, schema)["port"] == 1


def test_validate_settings_collects_all(load_exercise):
    m = load_exercise("ex06_settings_validation")
    schema = {"port": {"type": int, "min": 1, "max": 65535}, "mode": {"type": str, "choices": ["dev", "prod"], "required": True},
              "workers": {"type": int, "min": 1}, "name": {"type": str, "required": True}}
    with pytest.raises(m.ConfigError) as info:
        m.validate_settings({"port": 70000, "mode": "x", "workers": True, "zeta": 1, "alpha": 2}, schema)
    assert info.value.problems == ["port: maior que 65535", "mode: valor fora de ['dev', 'prod']", "workers: esperado int, recebido bool",
                                   "name: obrigatório", "alpha: chave desconhecida", "zeta: chave desconhecida"]
    assert "port: maior que 65535; mode" in str(info.value)
    with pytest.raises(m.ConfigError) as info:
        m.validate_settings({"port": "80", "workers": 0, "mode": "dev", "name": "x"}, schema)
    assert info.value.problems == ["port: esperado int, recebido str", "workers: menor que 1"]


def test_describe(load_exercise):
    describe = load_exercise("ex06_settings_validation").describe
    assert describe({"b": 2, "a": "x", "password": "s3"}, secret_keys={"password"}) == "a=x, b=2, password=***"
    assert describe({}) == ""
