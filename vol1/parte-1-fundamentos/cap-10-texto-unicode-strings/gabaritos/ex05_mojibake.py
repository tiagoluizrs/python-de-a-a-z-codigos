"""Gabarito do exercício 5."""


def fix_mojibake(text: str) -> str:
    for wrong in ("cp1252", "latin-1"):
        try:
            # desfaz a decodificação errada (volta aos bytes originais)...
            raw = text.encode(wrong)
        except UnicodeEncodeError:
            continue               # tem caractere que esse codec não gera
        try:
            # ...e decodifica do jeito certo
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            continue               # os bytes não formam UTF-8 válido
    return text                    # não parece mojibake: não mexa


def looks_like_mojibake(text: str) -> bool:
    return fix_mojibake(text) != text
