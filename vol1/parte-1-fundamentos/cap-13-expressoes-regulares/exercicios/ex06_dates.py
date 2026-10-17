"""Exercício 6: dd/mm/aaaa para ISO 8601 com sub e função."""


def dates_to_iso(text: str) -> str:
    """Troque cada data ``dd/mm/aaaa`` por ``aaaa-mm-dd``.

    Datas que não existem no calendário (``31/02/2026``) permanecem
    como estavam. Não troque números colados em outros (``112/10/2026``
    e ``12/10/20261`` não são datas). Dicas: ``\\b`` ou lookarounds,
    ``re.sub`` com função e ``datetime.date``.
    """
    raise NotImplementedError
