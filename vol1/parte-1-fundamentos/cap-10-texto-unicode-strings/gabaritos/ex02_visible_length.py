"""Gabarito do exercício 2."""
import unicodedata


def visible_length(text: str) -> int:
    # iter_graphemes (3.15) segue as regras do UAX #29
    return sum(1 for _ in unicodedata.iter_graphemes(text))


def truncate_visible(text: str, limit: int) -> str:
    if limit < 0:
        raise ValueError("limit must be >= 0")
    end = 0
    for count, cluster in enumerate(unicodedata.iter_graphemes(text)):
        if count == limit:
            break
        end = cluster.end          # Segment guarda start/end no texto
    return text[:end]


def approx_visible_length(text: str) -> int:
    """Versão aproximada, sem iter_graphemes (serve em Python < 3.15).

    Ignora combinantes (categoria Mn/Me), ZWJ, seletores de variação e o
    caractere que vem logo depois de um ZWJ. Erra bandeiras e outros casos.
    """
    count = 0
    glued = False                  # o anterior foi um ZWJ?
    for ch in text:
        if ch == "‍":
            glued = True
            continue
        if unicodedata.category(ch) in ("Mn", "Me") or ch in "️︎":
            continue
        if glued:
            glued = False
            continue
        count += 1
    return count
