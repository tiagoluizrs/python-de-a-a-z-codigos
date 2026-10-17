"""Exercício 2: tentativas com timeout por tentativa e espera exponencial."""
import asyncio  # noqa: F401


async def retry_async(factory, *, retries=3, delay=0.0, attempt_timeout=None, retry_on=(Exception,), sleep=asyncio.sleep):
    """Executa ``await factory()`` (``factory`` devolve uma NOVA corrotina a cada
    chamada), tentando de novo se levantar uma exceção de ``retry_on``.

    * no máximo ``1 + retries`` tentativas;
    * ``attempt_timeout`` (segundos, ou ``None``) limita CADA tentativa com
      ``asyncio.timeout``; estourar conta como falha (``TimeoutError``);
    * entre tentativas, ``await sleep(delay * 2**falhas_anteriores)`` (a primeira
      falha usa ``2**0``; ``delay=0`` não espera);
    * esgotadas as tentativas, re-levanta a ÚLTIMA exceção; exceções fora de
      ``retry_on`` sobem na hora;
    * ``retries < 0`` levanta ``ValueError``."""
    raise NotImplementedError
