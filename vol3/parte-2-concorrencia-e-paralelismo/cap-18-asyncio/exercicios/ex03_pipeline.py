"""Exercício 3: um pipeline produtor -> N trabalhadores com fila limitada."""


async def run_pipeline(items, worker, workers=3, queue_size=5):
    """Processa cada item com ``await worker(item)`` usando ``workers`` tarefas
    consumidoras e uma ``asyncio.Queue(maxsize=queue_size)``. Devolve os
    resultados NA ORDEM de ``items``.

    * ``items`` é um iterável comum e deve ser consumido AOS POUCOS pelo produtor
      (``await queue.put``), de modo que nunca haja muito mais que
      ``queue_size + workers`` itens "em voo" (contrapressão);
    * use ``asyncio.TaskGroup`` (uma falha cancela tudo e sobe como ``ExceptionGroup``);
    * ``workers < 1`` ou ``queue_size < 1`` levantam ``ValueError``;
    * ``items`` vazio devolve ``[]``."""
    raise NotImplementedError
