"""Exercício 3: diff de dois textos com ``difflib``."""


def text_diff(old: str, new: str) -> list[str]:
    """Devolva as linhas de um diff unificado entre ``old`` e ``new``.

    Use ``difflib.unified_diff`` com ``splitlines()``, os nomes de
    arquivo ``"old"`` e ``"new"`` e ``lineterm=""``.
    Textos iguais devolvem lista vazia.
    """
    raise NotImplementedError


def changed_lines(old: str, new: str) -> tuple[list[str], list[str]]:
    """Devolva ``(removidas, adicionadas)``: as linhas só do ``old`` e
    as linhas só do ``new`` (sem os prefixos ``-`` e ``+``), na ordem.
    Dica: filtre o diff ignorando os cabeçalhos ``---``, ``+++`` e ``@@``.
    """
    raise NotImplementedError


def closest(word: str, options: list[str]) -> str | None:
    """Sugestão "você quis dizer": a melhor opção parecida com ``word``
    (``difflib.get_close_matches`` com ``n=1``) ou ``None``."""
    raise NotImplementedError
