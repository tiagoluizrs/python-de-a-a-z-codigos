"""Gabarito do exercício 1."""
import unicodedata

ALLOWED = {" ", "-", "'"}


def normalize_name(name: str) -> str:
    # 1) NFC primeiro: depois dele, "e" + acento vira "é" (isalpha = True)
    text = unicodedata.normalize("NFC", name)
    # 2) split() sem argumento separa por QUALQUER espaço (inclui \t e
    #    U+00A0) e descarta pedaços vazios; join colapsa tudo em um ' '
    text = " ".join(text.split())
    if not text:
        raise ValueError("empty name")
    # 3) só letras, espaço, hífen e apóstrofo
    for ch in text:
        if not (ch.isalpha() or ch in ALLOWED):
            raise ValueError(f"invalid character {ch!r}")
    return text
