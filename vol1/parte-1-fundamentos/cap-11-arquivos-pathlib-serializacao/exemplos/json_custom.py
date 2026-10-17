"""JSON com tipos próprios: default= na ida, object_hook= na volta."""
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import PurePosixPath


@dataclass
class Invoice:
    number: int
    issued: date
    total: Decimal


def encode(obj):
    """Chamada só para objetos que o json não sabe converter."""
    if isinstance(obj, datetime):
        return {"__type__": "datetime", "value": obj.isoformat()}
    if isinstance(obj, date):
        return {"__type__": "date", "value": obj.isoformat()}
    if isinstance(obj, Decimal):
        return {"__type__": "decimal", "value": str(obj)}
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    if isinstance(obj, PurePosixPath):
        return obj.as_posix()
    if isinstance(obj, Invoice):
        return asdict(obj)
    raise TypeError(
        f"Object of type {type(obj).__name__} is not JSON serializable")


def decode(obj):
    """Chamada para cada objeto JSON, de dentro para fora."""
    kind = obj.get("__type__")
    if kind == "datetime":
        return datetime.fromisoformat(obj["value"])
    if kind == "date":
        return date.fromisoformat(obj["value"])
    if kind == "decimal":
        return Decimal(obj["value"])
    return obj


payload = {
    "when": datetime(2026, 10, 12, 9, 30),
    "tags": {"b", "a"},
    "path": PurePosixPath("/srv/data"),
    "invoice": Invoice(7, date(2026, 10, 1), Decimal("19.90")),
}
text = json.dumps(payload, default=encode, indent=2)
print(text)

back = json.loads(text, object_hook=decode)
print(back["when"], type(back["when"]).__name__)
print(back["invoice"]["issued"], back["invoice"]["total"])
print(back["invoice"]["total"] + Decimal("0.10"))
inv = Invoice(**back["invoice"])
print(type(inv).__name__, inv.total)

# Um tipo sem regra gera TypeError, em vez de gravar lixo em silêncio
try:
    json.dumps({"x": object()}, default=encode)
except TypeError as exc:
    print("TypeError:", exc)
