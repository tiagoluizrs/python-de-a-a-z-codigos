"""Gabarito do exercício 5."""
from collections.abc import Callable


def merge(base: dict, other: dict,
          on_conflict: Callable | None = None) -> dict:
    result = dict(base)                 # cópia rasa do nível atual
    for key, value in other.items():
        if key not in result:
            result[key] = value
        elif isinstance(result[key], dict) and isinstance(value, dict):
            # a recursão devolve um dict novo: os originais ficam intactos
            result[key] = merge(result[key], value, on_conflict)
        elif on_conflict is not None:
            result[key] = on_conflict(key, result[key], value)
        else:
            result[key] = value
    return result
