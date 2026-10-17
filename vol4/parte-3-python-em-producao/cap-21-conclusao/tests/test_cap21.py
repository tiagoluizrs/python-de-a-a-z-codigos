from pathlib import Path

import pytest

import readiness
import readiness_core

GOOD = {
    "pyproject.toml": '[project]\nname = "x"\nrequires-python = ">=3.15"\n',
    "uv.lock": "version = 1\n",
    "src/x/app.py": "import logging\nlog = logging.getLogger(__name__)\n",
    "tests/test_app.py": "def test_ok():\n    assert True\n",
    ".gitignore": ".venv/\n.env\n",
    "README.md": "# x\n",
}


def pairs(findings):
    return [(f.rule, f.severity) for f in findings]


# ---------- o verificador de exemplo (e a leitura do disco) ----------
def test_core_good_project_has_only_type_warning():
    findings = readiness_core.scan(GOOD)
    assert pairs(findings) == [("PR008", "aviso"), ("PR010", "aviso")]          # sem /healthz e sem verificador de tipos
    assert readiness_core.score(findings) == 90


def test_core_bad_project():
    bad = {"app.py": "PASSWORD = 'hunter2hunter2'\n", "Dockerfile": "FROM python\nENV API_TOKEN=abc\nCMD python app.py\n", ".env": "X=1\n"}
    rules = {f.rule for f in readiness_core.scan(bad)}
    assert {"PR001", "PR002", "PR003", "PR004", "PR005", "PR006", "PR007"} <= rules
    assert readiness_core.score(readiness_core.scan(bad)) == 0


def test_read_project_skips_junk(tmp_path):
    (tmp_path / "a.py").write_text("print(1)\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "x.py").write_text("junk", encoding="utf-8")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG\xff\xfe")
    files = readiness.read_project(tmp_path)
    assert set(files) == {"a.py", "logo.png"} and files["logo.png"] == ""


def test_chapter_projects_pass_the_gate():
    part7 = Path(__file__).resolve().parents[2]
    app = readiness.read_project(part7 / "cap-17-dockerizacao" / "exemplos" / "app")
    findings = readiness_core.scan(app)
    assert not any(f.rule in ("PR004", "PR005", "PR006", "PR007") for f in findings)       # o Dockerfile de produção do Capítulo 17 passa
    loja = readiness.read_project(part7 / "cap-18-arquitetura-projeto")
    assert not any(f.rule in ("PR001", "PR002", "PR003", "PR007") for f in readiness_core.scan(loja))


# ---------- ex01 ----------
def test_scan_project_good(load_exercise):
    m = load_exercise("ex01_readiness")
    assert m.scan_project(GOOD) == []


def test_scan_project_rules(load_exercise):
    m = load_exercise("ex01_readiness")
    assert pairs(m.scan_project({})) == [("PR001", "erro"), ("PR002", "erro"), ("PR003", "erro")]
    assert pairs(m.scan_project({**GOOD, "pyproject.toml": "[project]\nname = 'x'\n"})) == [("PR001", "erro")]
    no_lock = {k: v for k, v in GOOD.items() if k != "uv.lock"}
    assert pairs(m.scan_project(no_lock)) == [("PR002", "erro")]
    assert m.scan_project({**no_lock, "requirements.txt": "flask==3.1.0\n"}) == []
    assert pairs(m.scan_project({**no_lock, "requirements-dev.txt": "flask\n"})) == [("PR002", "erro")]
    assert m.scan_project({**GOOD, "tests/api_test.py": "", "tests/test_app.py": "x"}) == []
    only_test_dir = {k: v for k, v in GOOD.items() if k != "tests/test_app.py"}
    assert pairs(m.scan_project({**only_test_dir, "tests/conftest.py": ""})) == [("PR003", "erro")]


def test_scan_project_env_and_secrets(load_exercise):
    m = load_exercise("ex01_readiness")
    assert pairs(m.scan_project({**GOOD, ".gitignore": ".venv/\n"})) == [("PR006", "aviso")]
    assert m.scan_project({k: v for k, v in GOOD.items() if k != ".gitignore"}) == []
    assert pairs(m.scan_project({**GOOD, ".env": "A=1"})) == [("PR006", "erro")]
    secrets = {
        "a.py": 'token = "abc123xyz"\n', "b.yaml": "key: AKIAABCDEFGHIJKLMNOP\n", "c.toml": 'API-KEY = "segredo-bem-longo"\n',
        "d.json": '{"x": "-----BEGIN RSA PRIVATE KEY-----"}', "e.py": 'password = "curto"\n', "f.md": 'token = "abc123xyz"\n', "g.ini": "senha = 'abcdefg'\n",
    }
    found = m.scan_project({**GOOD, **secrets})
    assert pairs(found) == [("PR007", "erro")] * 5                                              # a, b, c, d e g; "curto" e o .md não contam
    assert pairs(m.scan_project({**GOOD, "x.py": 'DEFAULT_TOKEN = os.environ["TOKEN"]\n'})) == []
    ordered = m.scan_project({".gitignore": "", "a.py": 'token = "abcdefgh"'})
    assert [f.severity for f in ordered] == ["erro"] * (len(ordered) - 1) + ["aviso"] and ordered[-1].rule == "PR006"


def test_scan_dockerfile(load_exercise):
    m = load_exercise("ex01_readiness")
    good = (Path(readiness.__file__).parents[2] / "cap-17-dockerizacao" / "exemplos" / "app" / "Dockerfile").read_text(encoding="utf-8")
    assert m.scan_dockerfile(good) == []
    bad = "# comentário\nFROM python\nFROM python:latest AS builder\nFROM builder AS final\nENV db_password=x\nARG API_KEY\nENV KEYBOARD=us\nCMD python app.py\n"
    found = m.scan_dockerfile(bad)
    assert pairs(found) == [("PR004", "erro"), ("PR004", "aviso"), ("PR004", "erro"), ("PR004", "erro"), ("PR004", "erro"), ("PR004", "erro"), ("PR004", "erro")]
    assert [f.severity for f in found] == ["erro", "aviso", "erro", "erro", "erro", "erro", "erro"]
    ok = "FROM python:3.15-slim\nFROM scratch\nFROM gcr.io/distroless/cc@sha256:" + "a" * 64 + "\nUSER app\nHEALTHCHECK CMD true\n"
    assert m.scan_dockerfile(ok) == []
    assert pairs(m.scan_dockerfile("FROM registry.local:5000/app\nUSER x\nHEALTHCHECK none\n")) == [("PR004", "erro")]


def test_score_and_render(load_exercise):
    m = load_exercise("ex01_readiness")
    F = m.Finding
    findings = [F("PR001", "erro", "sem pyproject"), F("PR004", "aviso", "sem HEALTHCHECK")]
    assert m.score(findings) == 80 and m.score([]) == 100 and m.score([F("x", "erro")] * 10) == 0
    assert m.render(findings) == "[erro ] PR001 sem pyproject\n[aviso] PR004 sem HEALTHCHECK\nplacar: 80/100 (1 erros, 1 avisos)"
    assert m.render([]) == "placar: 100/100 (0 erros, 0 avisos)"
