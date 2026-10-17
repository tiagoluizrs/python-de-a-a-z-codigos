"""Exercício 5: detectar e corrigir mojibake simples."""


def fix_mojibake(text: str) -> str:
    """Desfaça o mojibake "UTF-8 lido como cp1252/Latin-1".

    O texto ``"Ação"`` salvo em UTF-8 e lido como Latin-1 vira
    ``"AÃ§Ã£o"``. Devolva o texto corrigido, ou o MESMO texto se ele
    não parecer mojibake (não adivinhe: se o conserto falhar, devolva
    o original).

        fix_mojibake("AÃ§Ã£o") == "Ação"
        fix_mojibake("coraÃ§Ã£o") == "coração"
        fix_mojibake("Ação") == "Ação"        # já está correto
        fix_mojibake("你好") == "你好"          # não cabe em Latin-1
        fix_mojibake("plain") == "plain"
        fix_mojibake("itâ€™s") == "it’s"      # variante cp1252

    Dica: tente ``text.encode("cp1252")`` e, se falhar, ``"latin-1"``;
    depois ``.decode("utf-8")``. Capture ``UnicodeError``.
    """
    raise NotImplementedError


def looks_like_mojibake(text: str) -> bool:
    """Diga se ``fix_mojibake(text)`` mudaria o texto."""
    raise NotImplementedError
