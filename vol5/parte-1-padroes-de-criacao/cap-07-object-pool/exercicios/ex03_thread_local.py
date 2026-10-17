"""Exercício 3: um recurso POR THREAD (``threading.local``), a alternativa sem pool quando o objeto não precisa ser dividido."""


class PerThread:
    """``PerThread(factory, close=None)``.

    * ``get()``: o recurso DESTA thread, criado com ``factory()`` na primeira chamada de cada thread; chamadas seguintes da mesma thread devolvem o
      MESMO objeto; threads diferentes recebem objetos diferentes;
    * ``count``: quantos recursos foram criados e ainda não fechados (de todas as threads);
    * ``close_all()``: chama ``close(recurso)`` (se houver) em TODOS os recursos criados, de qualquer thread (inclusive threads que já terminaram), e
      esquece todos: depois disso o ``get()`` de qualquer thread cria um recurso novo. Se um ``close`` levantar exceção, os demais ainda são fechados
      e a PRIMEIRA exceção é levantada no fim.
    Seguro para várias threads (o registro de recursos precisa de uma trava)."""

    def __init__(self, factory, close=None):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    @property
    def count(self) -> int:
        raise NotImplementedError

    def close_all(self) -> None:
        raise NotImplementedError
