"""Gabarito do exercício 4."""
import copy


def variant(obj, **changes):
    return copy.replace(obj, **changes)


def variants(base, field, values):
    return [variant(base, **{field: v}) for v in values]


def copy_matrix(m):
    out = []
    for row in m:
        if not isinstance(row, list):
            raise TypeError(f"linha inválida: {row!r}")
        out.append(row[:])
    return out


def copy_json(data):
    if data is None or isinstance(data, (str, int, float, bool)):
        return data
    if isinstance(data, list):
        return [copy_json(x) for x in data]
    if isinstance(data, dict):
        out = {}
        for key, value in data.items():
            if not isinstance(key, str):
                raise TypeError(f"chave inválida: {key!r}")
            out[key] = copy_json(value)
        return out
    raise TypeError(f"tipo não suportado: {type(data).__name__}")
