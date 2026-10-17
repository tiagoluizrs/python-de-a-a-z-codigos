"""Exercício 2: contar "caracteres visíveis" (grapheme clusters)."""


def visible_length(text: str) -> int:
    """Conte quantos caracteres o usuário VÊ em ``text``.

    ``len`` conta pontos de código. Aqui, ``"e\\u0301"`` tem 1 caractere
    visível, uma bandeira (dois indicadores regionais) tem 1, e uma
    família de emojis ligada por ZWJ (U+200D) tem 1.

    Exemplos::

        visible_length("abc") == 3
        visible_length("e\\u0301") == 1
        visible_length("\\U0001F1E7\\U0001F1F7") == 1
        visible_length("") == 0

    Dica: no Python 3.15 existe ``unicodedata.iter_graphemes``. Se quiser
    um desafio, faça também uma versão aproximada sem ela (some os
    caracteres que NÃO são combinantes, ZWJ ou seletores de variação).
    """
    raise NotImplementedError


def truncate_visible(text: str, limit: int) -> str:
    """Devolva os primeiros ``limit`` caracteres visíveis de ``text``.

    Nunca corte no meio de um cluster:
    ``truncate_visible("a\\u0301bc", 2) == "a\\u0301b"``.
    ``limit`` negativo levanta ``ValueError``.
    """
    raise NotImplementedError
