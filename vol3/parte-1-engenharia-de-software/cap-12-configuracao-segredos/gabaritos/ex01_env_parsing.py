"""Gabarito do exercício 1."""
import re


def as_bool(text, name="valor"):
    value = text.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off", ""}:
        return False
    raise ValueError(f"{name}: booleano inválido: {text!r}")


def as_int(text, name="valor", minimum=None, maximum=None):
    try:
        value = int(text.strip())
    except ValueError:
        raise ValueError(f"{name}: inteiro inválido: {text!r}") from None
    if minimum is not None and value < minimum:
        raise ValueError(f"{name}: menor que {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name}: maior que {maximum}")
    return value


def as_list(text, separator=",", cast=str):
    return [cast(item.strip()) for item in text.split(separator) if item.strip()]


UNITS = {"ms": 0.001, "s": 1, "m": 60, "h": 3600, "d": 86400}


def as_duration(text, name="valor"):
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(ms|s|m|h|d)?\s*", text)
    if not match:
        raise ValueError(f"{name}: duração inválida: {text!r}")
    return float(match.group(1)) * UNITS[match.group(2) or "s"]
