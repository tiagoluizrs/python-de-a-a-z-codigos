"""Exercício 4: um pool que adquire N recursos de forma atômica."""


class Pool:
    """Adquire os recursos de ``factories`` (callables que devolvem um
    context manager) como UM só gerenciador de contexto.

    * ``with Pool(factories) as resources:`` devolve a lista dos valores
      que cada ``__enter__`` produziu, na ordem;
    * na saída, os recursos são liberados na ORDEM INVERSA;
    * se a aquisição do k-ésimo falhar, os k-1 anteriores são liberados
      e a exceção sobe;
    * implemente ``__enter__``/``__exit__`` em uma classe, guardando um
      ``ExitStack`` interno (``pop_all`` e ``close`` ajudam).
    """

    def __init__(self, factories):
        raise NotImplementedError
