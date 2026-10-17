"""Exercício 1: executar muitas corrotinas com um limite de simultâneas."""


async def gather_limited(factories, limit):
    """``factories`` é uma lista de callables SEM argumentos, cada um devolvendo
    uma corrotina (``lambda: fetch(url)``). Executa todas de forma CONCORRENTE,
    mas com NO MÁXIMO ``limit`` rodando ao mesmo tempo (``asyncio.Semaphore``), e
    devolve a lista de resultados NA ORDEM de ``factories``.

    * use ``asyncio.TaskGroup``: se alguma falhar, as demais são canceladas e o
      ``ExceptionGroup`` se propaga;
    * lista vazia devolve ``[]``; ``limit < 1`` levanta ``ValueError``."""
    raise NotImplementedError
