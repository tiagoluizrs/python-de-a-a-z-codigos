"""Gabarito do exercício 2."""
import re

SENSITIVE_KEYS = {"password", "senha", "token", "authorization", "api_key", "cpf", "card_number", "secret"}
_BEARER = re.compile(r"Bearer\s+[A-Za-z0-9._\-]+")
_EMAIL = re.compile(r"\b([A-Za-z0-9._%+\-])[A-Za-z0-9._%+\-]*@([A-Za-z0-9.\-]+\.[A-Za-z]{2,})\b")


def _clean_text(text: str, max_len: int) -> str:
    text = _BEARER.sub("Bearer ***", text)
    text = _EMAIL.sub(lambda m: f"{m.group(1)}***@{m.group(2)}", text)
    if len(text) > max_len:
        return f"{text[:max_len]}…(+{len(text) - max_len} chars)"
    return text


def redact(value, max_len=200):
    if isinstance(value, dict):
        return {k: "***" if isinstance(k, str) and k.lower() in SENSITIVE_KEYS else redact(v, max_len) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, max_len) for v in value]
    if isinstance(value, tuple):
        return tuple(redact(v, max_len) for v in value)
    if isinstance(value, str):
        return _clean_text(value, max_len)
    return value


def redact_event(logger, method, event_dict):
    return redact(event_dict)
