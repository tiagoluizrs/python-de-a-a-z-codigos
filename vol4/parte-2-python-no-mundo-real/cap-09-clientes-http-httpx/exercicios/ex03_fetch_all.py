"""Exercício 3: muitas requisições concorrentes, com limite e sem perder o resultado de ninguém."""


async def fetch_all(client, urls, *, concurrency=10):
    """Faz ``GET`` em cada URL com um ``httpx.AsyncClient`` COMPARTILHADO, no máximo ``concurrency`` ao mesmo tempo
    (``asyncio.Semaphore``). Devolve uma lista NA ORDEM de ``urls`` onde cada item é a ``httpx.Response`` ou a
    EXCEÇÃO (``httpx.RequestError``) daquela URL: um erro NÃO cancela as outras.

    * status 4xx/5xx NÃO são exceções aqui: vêm como ``Response`` (o chamador decide);
    * ``urls`` vazio devolve ``[]``; ``concurrency < 1`` levanta ``ValueError``."""
    raise NotImplementedError
