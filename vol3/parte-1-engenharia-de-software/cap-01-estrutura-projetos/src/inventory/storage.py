"""Persistência em JSON (a única parte do pacote que toca o disco)."""
import json
from pathlib import Path

from .core import Inventory, Item


def load(path):
    path = Path(path)
    if not path.exists():
        return Inventory()
    data = json.loads(path.read_text(encoding="utf-8"))
    return Inventory(Item(**row) for row in data)


def save(inventory, path):
    rows = [{"sku": i.sku, "name": i.name, "qty": i.qty} for i in inventory.items()]
    Path(path).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
