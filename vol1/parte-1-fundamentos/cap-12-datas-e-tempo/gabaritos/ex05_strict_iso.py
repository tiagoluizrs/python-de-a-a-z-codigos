"""Gabarito do exercício 5."""
import datetime as dt
import re

SHAPE = re.compile(
    r"\d{4}-\d{2}-\d{2}"        # data estendida
    r"T\d{2}:\d{2}:\d{2}"       # T maiúsculo e segundos obrigatórios
    r"(?:\.\d{1,6})?"           # fração opcional (até microssegundos)
    r"(Z|[+-]\d{2}:\d{2})?"     # fuso: capturado para checar a falta
)


def parse_strict(text: str) -> dt.datetime:
    if not isinstance(text, str):
        raise ValueError(f"expected str, got {type(text).__name__}")
    match = SHAPE.fullmatch(text)
    if match is None:
        raise ValueError(
            f"{text!r}: not in the form YYYY-MM-DDTHH:MM:SS[.ffffff]"
            " (extended format, uppercase 'T', seconds required)"
        )
    if match.group(1) is None:
        raise ValueError(f"{text!r}: missing UTC offset (Z or +HH:MM)")
    try:
        return dt.datetime.fromisoformat(text)
    except ValueError as error:   # data impossível, hora 25 etc.
        raise ValueError(
            f"{text!r}: invalid date or time ({error})") from error
