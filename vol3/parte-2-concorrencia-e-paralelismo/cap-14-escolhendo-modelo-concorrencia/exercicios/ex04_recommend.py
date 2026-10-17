"""Exercício 4: recomendar o modelo de concorrência."""


def recommend(cpu_bound, items, async_library=False, shared_state=False):
    """Devolve UM destes textos (exatamente):

    * ``"none"``: ``items <= 1``;
    * CPU (``cpu_bound``): ``"free-threading"`` se ``shared_state``, senão ``"processes"``;
    * E/S: ``"asyncio"`` se ``async_library`` e ``items > 500``; senão ``"threads"``.

    ``items`` negativo levanta ``ValueError``."""
    raise NotImplementedError


def explain(cpu_bound, items, async_library=False, shared_state=False):
    """Uma frase em português que justifica a recomendação: deve CITAR a
    recomendação e o motivo (``"CPU"``/``"E/S"``, o número de itens). Formato:
    ``"<modelo>: carga de <CPU|E/S> com <items> itens"`` (para ``none``:
    ``"none: nada a paralelizar"``)."""
    raise NotImplementedError
