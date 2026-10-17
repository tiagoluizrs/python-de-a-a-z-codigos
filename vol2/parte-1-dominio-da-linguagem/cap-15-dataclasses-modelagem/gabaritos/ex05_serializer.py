"""Gabarito do exercício 5."""
import dataclasses
import datetime as dt
from decimal import Decimal
from enum import Enum


def to_primitive(value):
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        result = {}
        for field in dataclasses.fields(value):
            if field.metadata.get("skip"):
                continue
            key = field.metadata.get("name", field.name)
            result[key] = to_primitive(getattr(value, field.name))
        return result
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [to_primitive(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [to_primitive(item) for item in sorted(value, key=str)]
    if isinstance(value, dict):
        return {str(key): to_primitive(item) for key, item in value.items()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"não serializável: {type(value).__name__}")
