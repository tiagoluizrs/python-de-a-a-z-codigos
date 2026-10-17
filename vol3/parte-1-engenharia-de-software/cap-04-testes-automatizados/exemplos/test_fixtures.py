"""Fixtures: preparação, limpeza, escopos, tmp_path, monkeypatch, capsys e caplog."""
import logging
import os

import pytest

from conftest import CALLS


@pytest.fixture
def resource():
    CALLS.append("setup")
    yield "recurso"                       # o teste roda aqui
    CALLS.append("teardown")              # limpeza: roda mesmo se o teste falhar


def test_fixture_setup_and_teardown(resource):
    assert resource == "recurso"
    assert CALLS[-1] == "setup"


def test_teardown_ran_after_previous_test():
    assert CALLS.count("teardown") >= 1


CREATED = []


@pytest.fixture(scope="module")
def expensive():
    CREATED.append("criada")              # roda UMA vez por módulo
    return object()


def test_module_scope_first(expensive):
    assert len(CREATED) == 1


def test_module_scope_second(expensive):
    assert len(CREATED) == 1              # a mesma instância serviu aos dois testes


@pytest.fixture
def make_user():
    """Fábrica: a fixture devolve uma função para criar quantos objetos o teste quiser."""
    created = []

    def factory(name, admin=False):
        user = {"name": name, "admin": admin}
        created.append(user)
        return user

    yield factory
    assert len(created) <= 3              # verificação na limpeza


def test_factory_fixture(make_user):
    ana, bia = make_user("ana"), make_user("bia", admin=True)
    assert ana["admin"] is False and bia["admin"] is True


@pytest.fixture(params=["sqlite", "memory"])
def backend(request):
    """Fixture parametrizada: cada teste que a usa roda uma vez por parâmetro."""
    return request.param


def test_runs_per_backend(backend):
    assert backend in {"sqlite", "memory"}


def test_tmp_path_is_unique_and_clean(tmp_path):
    assert list(tmp_path.iterdir()) == []
    (tmp_path / "dados.txt").write_text("olá", encoding="utf-8")
    assert (tmp_path / "dados.txt").read_text(encoding="utf-8") == "olá"


def test_monkeypatch_env_and_attr(monkeypatch):
    monkeypatch.setenv("APP_MODE", "teste")
    assert os.environ["APP_MODE"] == "teste"
    monkeypatch.setattr(os, "getcwd", lambda: "/falso")
    assert os.getcwd() == "/falso"
    monkeypatch.delenv("APP_MODE")
    assert "APP_MODE" not in os.environ


def test_monkeypatch_is_undone():
    assert "APP_MODE" not in os.environ and os.getcwd() != "/falso"


def test_capsys_captures_output(capsys):
    print("olá stdout")
    print("olá stderr", file=__import__("sys").stderr)
    captured = capsys.readouterr()
    assert captured.out == "olá stdout\n" and captured.err == "olá stderr\n"


def test_caplog_captures_logs(caplog):
    with caplog.at_level(logging.INFO):
        logging.getLogger("meuapp").info("pedido %s criado", 42)
        logging.getLogger("meuapp").debug("detalhe")
    assert "pedido 42 criado" in caplog.text
    assert [r.levelname for r in caplog.records] == ["INFO"]


def test_filled_cart_fixture_from_conftest(filled_cart):
    assert filled_cart.total() == 25.5


@pytest.mark.slow
def test_marked_slow():
    assert sum(range(10_000)) == 49_995_000
