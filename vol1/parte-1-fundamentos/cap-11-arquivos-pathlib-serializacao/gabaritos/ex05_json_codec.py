"""Gabarito do exercício 5."""
import json
from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import get_type_hints


@dataclass
class Order:
    id: int
    customer: str
    total: Decimal
    created: datetime
    due: date


def _default(obj):
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if isinstance(obj, Decimal):
        return str(obj)             # texto: sem perda de precisão
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} "
                    "is not JSON serializable")


def dumps(obj) -> str:
    return json.dumps(obj, default=_default, sort_keys=True)


def loads_as(cls, text: str):
    raw = json.loads(text)
    hints = get_type_hints(cls)
    values = {}
    for field in fields(cls):
        value = raw[field.name]     # KeyError se faltar
        kind = hints[field.name]
        if kind is Decimal:
            value = Decimal(value)
        elif kind is datetime:
            value = datetime.fromisoformat(value)
        elif kind is date:
            value = date.fromisoformat(value)
        values[field.name] = value
    return cls(**values)
