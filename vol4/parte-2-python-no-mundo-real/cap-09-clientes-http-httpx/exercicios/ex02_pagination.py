"""Exercício 2: paginação preguiçosa, síncrona e assíncrona."""


def paginate(client, url, params=None, *, items_key="items", next_key="next", page_param="page", start=1, max_pages=None):
    """Gerador que percorre uma API paginada. Cada resposta é JSON com a lista em ``items_key`` e o número da
    PRÓXIMA página em ``next_key`` (``None`` na última). Faz ``GET url`` com ``params`` mais ``{page_param: página}``,
    chama ``raise_for_status()`` e entrega os itens UM A UM.

    * preguiçoso: só pede a página seguinte quando o consumidor termina a atual;
    * ``max_pages`` limita quantas páginas pedir (``None`` = sem limite);
    * ``params`` do chamador NÃO pode ser alterado."""
    raise NotImplementedError


async def apaginate(client, url, params=None, *, items_key="items", next_key="next", page_param="page", start=1, max_pages=None):
    """Versão assíncrona (``httpx.AsyncClient``): gerador assíncrono com o mesmo contrato."""
    raise NotImplementedError
    yield  # pragma: no cover
