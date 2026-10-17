"""Dublês de teste: fakes, stubs e mocks; injeção de dependência."""
from decimal import Decimal
from unittest import mock

import pytest

from pricing import fetch_rate


# 1) FAKE: uma implementação simples e funcional, escrita por você
class FakeHttp:
    def __init__(self, responses):
        self.responses = responses
        self.requested = []

    def get_json(self, url):
        self.requested.append(url)
        return self.responses[url]


def test_fetch_rate_with_fake():
    client = FakeHttp({"https://api.example.com/rates/USD": {"rate": 5.25}})
    assert fetch_rate(client, "USD") == Decimal("5.25")
    assert client.requested == ["https://api.example.com/rates/USD"]


# 2) MOCK: registra chamadas e permite verificá-las
def test_fetch_rate_with_mock():
    client = mock.Mock()
    client.get_json.return_value = {"rate": 4.8}
    assert fetch_rate(client, "EUR") == Decimal("4.8")
    client.get_json.assert_called_once_with("https://api.example.com/rates/EUR")


def test_mock_side_effect_raises():
    client = mock.Mock()
    client.get_json.side_effect = ConnectionError("fora do ar")
    with pytest.raises(ConnectionError):
        fetch_rate(client, "USD")


def test_missing_rate_key():
    client = mock.Mock()
    client.get_json.return_value = {"erro": "moeda desconhecida"}
    with pytest.raises(KeyError, match="rate"):
        fetch_rate(client, "XXX")


# 3) spec: o mock imita a interface real e recusa o que ela não tem
class RealClient:
    def get_json(self, url):
        raise NotImplementedError


def test_mock_without_spec_hides_typos():
    loose = mock.Mock()
    loose.get_jsno("x")                                  # typo aceito em silêncio!
    strict = mock.Mock(spec=RealClient)
    with pytest.raises(AttributeError):
        strict.get_jsno("x")


def test_autospec_checks_signature():
    client = mock.create_autospec(RealClient, instance=True)
    client.get_json.return_value = {"rate": 1}
    fetch_rate(client, "USD")
    with pytest.raises(TypeError):
        client.get_json()                                # faltou o argumento url


# 4) patch: troca um nome DURANTE o teste (onde ele é USADO)
def test_patch_replaces_name(monkeypatch):
    import pricing

    with mock.patch.object(pricing, "Decimal", side_effect=lambda v: f"D({v})"):
        assert pricing.fetch_rate(FakeHttp({"https://api.example.com/rates/X": {"rate": 2}}), "X") == "D(2)"
    assert pricing.Decimal is Decimal                    # restaurado ao sair do with


# 5) Relógio injetado: sem congelar o tempo global
def test_clock_injection():
    from datetime import date
    from pricing import days_until
    assert days_until(date(2026, 1, 2), today=date(2026, 1, 1)) == 1
