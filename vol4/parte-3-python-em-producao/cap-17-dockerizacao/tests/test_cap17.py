import signal
import threading
import time
from pathlib import Path

import pytest

APP = Path(__file__).parent.parent / "exemplos" / "app"


# ---------- ex01 ----------
def rules(findings):
    return [(f.rule, f.line) for f in findings]


def test_lint_naive_dockerfile(load_exercise):
    m = load_exercise("ex01_dockerfile_lint")
    text = """# o jeito errado
FROM python
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt && \\
    apt-get install -y curl
ENV API_TOKEN=abc
ADD ./config /etc/config
ADD https://exemplo.com/x.tar.gz /tmp/
CMD python app.py
"""
    found = rules(m.lint(text))
    assert found == [("DL001", 2), ("DL002", 2), ("DL009", 2), ("DL004", 4), ("DL005", 5), ("DL006", 5), ("DL008", 7), ("DL007", 8), ("DL003", 10)] or \
        sorted(found) == sorted([("DL001", 2), ("DL002", 2), ("DL009", 2), ("DL004", 4), ("DL005", 5), ("DL006", 5), ("DL008", 7), ("DL007", 8), ("DL003", 10)])
    assert [f.line for f in m.lint(text)] == sorted(f.line for f in m.lint(text))                # ordenado por linha


def test_lint_good_dockerfile(load_exercise):
    m = load_exercise("ex01_dockerfile_lint")
    good = (APP / "Dockerfile").read_text(encoding="utf-8")
    assert m.lint(good) == []                                                                       # o Dockerfile do capítulo passa limpo
    slim = (APP / "Dockerfile.slim").read_text(encoding="utf-8")
    assert sorted(f.rule for f in m.lint(slim)) == ["DL002", "DL009"]                              # slim: sem USER e sem HEALTHCHECK
    naive = (APP / "Dockerfile.naive").read_text(encoding="utf-8")
    assert {"DL002", "DL003", "DL004", "DL005", "DL009"} <= {f.rule for f in m.lint(naive)} and "DL001" not in {f.rule for f in m.lint(naive)}


def test_lint_from_rules(load_exercise):
    m = load_exercise("ex01_dockerfile_lint")
    base = "USER app\nHEALTHCHECK CMD true\n"
    for image, expected in [("python:3.15-slim", []), ("python:latest", ["DL001"]), ("python", ["DL001"]), ("scratch", []),
                            ("python@sha256:" + "a" * 64, []), ("registry.local:5000/app", ["DL001"]), ("registry.local:5000/app:1.2", [])]:
        assert [f.rule for f in m.lint(f"FROM {image}\n" + base)] == expected, image
    stages = "FROM python:3.15 AS builder\nRUN true\nFROM builder AS final\nUSER x\nHEALTHCHECK CMD true\n"
    assert m.lint(stages) == []
    assert m.lint("RUN echo sem from\n") == []


def test_lint_rules_details(load_exercise):
    m = load_exercise("ex01_dockerfile_lint")
    head = "FROM python:3.15-slim\nUSER app\nHEALTHCHECK CMD true\n"
    assert [f.rule for f in m.lint(head + "RUN --mount=type=cache,target=/root/.cache pip install x\n")] == []
    assert [f.rule for f in m.lint(head + "RUN pip install --no-cache-dir x\n")] == []
    assert [f.rule for f in m.lint(head + "RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*\n")] == []
    assert [f.rule for f in m.lint(head + "CMD [\"python\", \"app.py\"]\nENTRYPOINT [\"x\"]\n")] == []
    assert [(f.rule, f.line) for f in m.lint(head + "ENTRYPOINT /run.sh\n")] == [("DL003", 4)]
    assert [f.rule for f in m.lint(head + "ARG BUILD_SECRET\nENV db_password=x\nENV KEYBOARD_LAYOUT=us\n")] == ["DL008", "DL008", "DL008"]
    copy_ok = head + "COPY pyproject.toml ./\nRUN uv sync\nCOPY . .\n"
    assert m.lint(copy_ok) == []
    assert [(f.rule, f.line) for f in m.lint(head + "COPY . /app\nRUN npm install\nRUN pip install -e .\n")][:1] == [("DL004", 4)]


# ---------- ex02 ----------
def test_dockerignore_basics(load_exercise):
    m = load_exercise("ex02_dockerignore")
    pats = [".git", "*.pyc", "__pycache__", "# comentário", "", "  .env  ", "node_modules", "**/*.log", "build/"]
    ignored = [".git/config", "a.pyc", ".env", "node_modules/x/y.js", "debug.log", "a/b/c/debug.log", "build/out.bin", "__pycache__/x.pyc"]
    kept = ["src/main.py", "src/__pycache__/x.cpython.pyc.txt", "docs/node_modules/readme.md", "README.md", ".envrc", "sub/a.pyc.bak"]
    for path in ignored:
        assert m.is_ignored(path, pats), path
    for path in kept:
        assert not m.is_ignored(path, pats), path
    assert m.is_ignored("sub/a.pyc", pats) is False                      # *.pyc é ancorado na raiz: não casa em subpastas


def test_dockerignore_globs_and_negation(load_exercise):
    m = load_exercise("ex02_dockerignore")
    assert m.is_ignored("a.pyc", ["**/*.pyc"]) and m.is_ignored("x/y/a.pyc", ["**/*.pyc"]) and not m.is_ignored("a.pyc.txt", ["**/*.pyc"])
    assert m.is_ignored("a1.txt", ["a?.txt"]) and not m.is_ignored("a12.txt", ["a?.txt"]) and not m.is_ignored("a/.txt", ["a?.txt"])
    assert m.is_ignored("docs/a.md", ["docs/*.md"]) and not m.is_ignored("docs/x/a.md", ["docs/*.md"])
    assert m.is_ignored("docs/x/a.md", ["docs/**/*.md"]) and m.is_ignored("docs/a.md", ["docs/**/*.md"])
    assert m.is_ignored("build/x", ["/build"]) and m.is_ignored("build/x", ["build/"])
    pats = ["*.md", "!README.md"]
    assert m.is_ignored("CHANGES.md", pats) and not m.is_ignored("README.md", pats)
    assert m.is_ignored("README.md", ["!README.md", "*.md"])              # vale a ÚLTIMA regra que casa
    assert not m.is_ignored("x", [])


def test_build_context(load_exercise):
    m = load_exercise("ex02_dockerignore")
    paths = ["Dockerfile", ".git/HEAD", "src/a.py", "src/a.pyc", ".env", "README.md", "tests/t.py"]
    assert m.build_context(paths, [".git", "**/*.pyc", ".env", "tests"]) == ["Dockerfile", "src/a.py", "README.md"]


# ---------- ex03 ----------
INS = [("FROM", "python:3.15-slim"), ("COPY", "pyproject.toml uv.lock ./"), ("RUN", "uv sync --no-install-project"),
       ("COPY", "src ./src"), ("RUN", "uv sync"), ("CMD", '["shop-api"]')]


def test_first_invalidated(load_exercise):
    m = load_exercise("ex03_cache_planner")
    assert m.first_invalidated(INS, {"src/shop_api/server.py"}) == 3
    assert m.first_invalidated(INS, {"uv.lock"}) == 1
    assert m.first_invalidated(INS, {"README.md"}) is None and m.first_invalidated(INS, set()) is None
    assert m.first_invalidated(INS, {"srcx/a.py"}) is None                                      # "srcx" não está DENTRO de "src"
    naive = [("FROM", "x"), ("COPY", ". ."), ("RUN", "pip install .")]
    assert m.first_invalidated(naive, {"qualquer/coisa.py"}) == 1
    assert m.first_invalidated([("COPY", "--chown=app:app a.txt b/ /dst/")], {"b/x"}) == 0


def test_rebuild_cost_and_order(load_exercise):
    m = load_exercise("ex03_cache_planner")
    seconds = [0.0, 0.5, 12.0, 0.2, 3.0, 0.0]
    assert m.rebuild_cost(INS, seconds, {"src/a.py"}) == pytest.approx(3.2)
    assert m.rebuild_cost(INS, seconds, {"uv.lock"}) == pytest.approx(15.7)
    assert m.rebuild_cost(INS, seconds, {"docs/x.md"}) == 0.0
    with pytest.raises(ValueError):
        m.rebuild_cost(INS, [1.0], {"x"})
    block = [("FROM", "x"), ("COPY", "src ./src"), ("COPY", "pyproject.toml ./"), ("COPY", "README.md ./"), ("RUN", "build"), ("COPY", "a b/"), ("COPY", "z y/")]
    freq = {"src": 10.0, "pyproject.toml": 0.1, "README.md": 0.3, "a": 5.0, "z": 1.0}
    assert m.best_order(block, freq) == [("FROM", "x"), ("COPY", "pyproject.toml ./"), ("COPY", "README.md ./"), ("COPY", "src ./src"), ("RUN", "build"),
                                          ("COPY", "z y/"), ("COPY", "a b/")]
    assert m.best_order([("COPY", "x ./"), ("COPY", "y ./")], {}) == [("COPY", "x ./"), ("COPY", "y ./")]


# ---------- ex04 ----------
def test_graceful_shutdown_flags_and_restore(load_exercise):
    m = load_exercise("ex04_graceful")
    original = signal.getsignal(signal.SIGTERM)
    with m.GracefulShutdown() as shutdown:
        assert shutdown.requested is False and shutdown.signal_name is None and shutdown.wait(0.01) is False
        assert signal.getsignal(signal.SIGTERM) != original
        signal.raise_signal(signal.SIGTERM)
        assert shutdown.requested and shutdown.signal_name == "SIGTERM" and shutdown.wait(0.01) is True
        signal.raise_signal(signal.SIGINT)
        assert shutdown.signal_name == "SIGTERM"                                  # o PRIMEIRO sinal manda
    assert signal.getsignal(signal.SIGTERM) == original


def test_graceful_restores_on_exception(load_exercise):
    m = load_exercise("ex04_graceful")
    original = signal.getsignal(signal.SIGINT)
    with pytest.raises(RuntimeError):
        with m.GracefulShutdown():
            raise RuntimeError("boom")
    assert signal.getsignal(signal.SIGINT) == original


def test_serve_finishes_items_and_stops(load_exercise):
    m = load_exercise("ex04_graceful")
    done = []
    with m.GracefulShutdown() as shutdown:
        def handle(item):
            done.append(item)
            if item == 3:
                signal.raise_signal(signal.SIGTERM)                              # o pedido chega DURANTE o item 3
        result = m.serve(handle, shutdown, list(range(1, 8)))
    assert done == [1, 2, 3] and result == {"handled": 3, "left": 4, "reason": "SIGTERM", "late": False}


def test_serve_done_and_late(load_exercise):
    m = load_exercise("ex04_graceful")
    with m.GracefulShutdown() as shutdown:
        assert m.serve(lambda i: None, shutdown, [1, 2]) == {"handled": 2, "left": 0, "reason": "done", "late": False}
    with m.GracefulShutdown() as shutdown:
        def slow(item):
            signal.raise_signal(signal.SIGINT)
            time.sleep(0.15)
        result = m.serve(slow, shutdown, [1, 2, 3], grace_seconds=0.05)
    assert result == {"handled": 1, "left": 2, "reason": "SIGINT", "late": True}


def test_wait_times_out_without_burning_cpu(load_exercise):
    m = load_exercise("ex04_graceful")
    with m.GracefulShutdown() as shutdown:
        cpu_start, start = time.process_time(), time.perf_counter()
        assert shutdown.wait(0.3) is False
        assert time.perf_counter() - start >= 0.29
        assert time.process_time() - cpu_start < 0.15                          # esperou dormindo, não em um laço ocupado


# ---------- ex05 ----------
SPEC = {"PORT": {"type": int, "default": 8000}, "DEBUG": {"type": bool, "default": False}, "DB_URL": {}, "DB_PASSWORD": {"secret": True},
        "RATE": {"type": float, "default": 1.5}}


def files(mapping):
    return lambda path: mapping[path]


def test_config_values_and_defaults(load_exercise):
    m = load_exercise("ex05_env_config")
    spec = {**SPEC, "DB_PASSWORD": {"secret": True, "read_file": files({"/run/secrets/db": "s3cr3t\n\n"})}}
    env = {"PORT": "9000", "DEBUG": "Yes", "DB_URL": "postgres://x", "DB_PASSWORD_FILE": "/run/secrets/db"}
    config = m.load_config(env, spec)
    assert config == {"PORT": 9000, "DEBUG": True, "DB_URL": "postgres://x", "DB_PASSWORD": "s3cr3t", "RATE": 1.5} and list(config) == list(spec)
    assert m.load_config({"DB_URL": "u", "DB_PASSWORD": "p"}, SPEC)["PORT"] == 8000


def test_config_reports_all_problems(load_exercise):
    m = load_exercise("ex05_env_config")
    env = {"PORT": "abc", "DEBUG": "talvez", "RATE": "1,5", "DB_PASSWORD": "a", "DB_PASSWORD_FILE": "/x"}
    with pytest.raises(m.ConfigError) as info:
        m.load_config(env, SPEC)
    assert info.value.problems == ["PORT: valor inválido 'abc' para int", "DEBUG: valor inválido 'talvez' para bool", "DB_URL: obrigatória",
                                   "DB_PASSWORD: defina DB_PASSWORD ou DB_PASSWORD_FILE, não os dois", "RATE: valor inválido '1,5' para float"]
    assert "obrigatória" in str(info.value)


@pytest.mark.parametrize("text,expected", [("1", True), ("TRUE", True), ("on", True), ("0", False), ("No", False), ("OFF", False)])
def test_config_bool_forms(load_exercise, text, expected):
    m = load_exercise("ex05_env_config")
    assert m.load_config({"DEBUG": text}, {"DEBUG": {"type": bool}})["DEBUG"] is expected


def test_describe_masks_secrets(load_exercise):
    m = load_exercise("ex05_env_config")
    config = m.load_config({"DB_URL": "u", "DB_PASSWORD": "hunter2"}, SPEC)
    text = m.describe(config, SPEC)
    assert "hunter2" not in text and text.splitlines() == ["PORT=8000", "DEBUG=False", "DB_URL=u", "DB_PASSWORD=***", "RATE=1.5"]


# ---------- ex06 ----------
STACK = {"db": {}, "redis": {}, "migrate": {"depends_on": ["db"]}, "api": {"depends_on": {"db": {"condition": "service_healthy"}, "redis": {}, "migrate": {}}},
         "worker": {"depends_on": ["redis", "migrate"]}, "proxy": {"depends_on": ["api"]}}


def test_startup_waves(load_exercise):
    m = load_exercise("ex06_compose_order")
    assert m.startup_waves(STACK) == [["db", "redis"], ["migrate"], ["api", "worker"], ["proxy"]]
    assert m.startup_waves({}) == []
    assert m.startup_waves({"b": {}, "a": {}}) == [["a", "b"]]


def test_startup_errors(load_exercise):
    m = load_exercise("ex06_compose_order")
    with pytest.raises(ValueError, match="web depende de cache, que não existe"):
        m.startup_waves({"web": {"depends_on": ["cache"]}})
    with pytest.raises(ValueError, match="ciclo: a -> b -> c -> a"):
        m.startup_waves({"c": {"depends_on": ["a"]}, "a": {"depends_on": ["b"]}, "b": {"depends_on": ["c"]}, "ok": {}})
    with pytest.raises(ValueError, match="ciclo: x -> x"):
        m.startup_waves({"x": {"depends_on": ["x"]}})


def test_shutdown_order_and_dependents(load_exercise):
    m = load_exercise("ex06_compose_order")
    assert m.shutdown_order(STACK) == ["proxy", "api", "worker", "migrate", "db", "redis"]
    assert m.dependents_of(STACK, "db") == ["api", "migrate", "proxy", "worker"]
    assert m.dependents_of(STACK, "api") == ["proxy"] and m.dependents_of(STACK, "proxy") == []
    with pytest.raises(ValueError):
        m.dependents_of(STACK, "nada")
