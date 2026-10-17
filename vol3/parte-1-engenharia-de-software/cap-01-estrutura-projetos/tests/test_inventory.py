"""Testes do PRÓPRIO projeto: ficam fora de src/ e importam o pacote instalado."""
import pytest

import inventory
from inventory import Inventory, Item, OutOfStockError
from inventory.cli import main


def test_public_api():
    assert set(inventory.__all__) == {"Inventory", "Item", "OutOfStockError", "__version__"}
    assert inventory.__version__ != "0+unknown"                  # pacote instalado: versão do pyproject


def test_inventory_rules():
    stock = Inventory([Item(" ab1 ", "Parafuso", 10)])
    stock.add(Item("AB1", "Parafuso", 5))
    stock.remove("ab1", 3)
    assert stock.items() == [Item("AB1", "Parafuso", 12)] and stock.total_quantity() == 12
    with pytest.raises(OutOfStockError):
        stock.remove("AB1", 99)
    with pytest.raises(ValueError):
        Item("x", "y", -1)


def test_cli_roundtrip(tmp_path, capsys):
    data = str(tmp_path / "stock.json")
    assert main(["--file", data, "add", "a1", "Porca", "7"]) == 0
    assert main(["--file", data, "remove", "a1", "2"]) == 0
    assert main(["--file", data, "remove", "a1", "50"]) == 1
    assert main(["--file", data, "list"]) == 0
    out = capsys.readouterr()
    assert "A1" in out.out and "total: 5" in out.out and "estoque insuficiente" in out.err
