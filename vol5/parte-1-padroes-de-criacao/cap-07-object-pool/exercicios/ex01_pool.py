"""Exercício 1: um pool de objetos completo: criação sob demanda, espera com limite de tempo, validação, reset e fechamento."""


class PoolExhausted(TimeoutError):
    """Nenhum objeto livre dentro do tempo dado."""


class Pool:
    """``Pool(factory, size, *, reset=None, validate=None, close=None)``: no máximo ``size`` objetos (``size >= 1``, senão ``ValueError``).

    * criação SOB DEMANDA: ``factory()`` só é chamada quando alguém pede e não há objeto ocioso, até ``size`` criados no total;
    * ``acquire(timeout=None)``: devolve um objeto ocioso (o mais antigo primeiro, FIFO) ou cria um novo; se o limite foi atingido e todos estão
      emprestados, ESPERA até ``timeout`` segundos (``None`` espera para sempre) e, estourado o tempo, ``PoolExhausted(f"nenhum objeto livre em {timeout}s")``.
      Se ``validate`` foi dado e devolve falso para um objeto ocioso, ele é DESCARTADO (chama ``close(obj)`` se houver, ``created`` diminui,
      ``discarded`` aumenta) e a busca continua;
    * ``release(obj)``: chama ``reset(obj)`` (se houver) e devolve o objeto ao pool, acordando quem espera. Objeto que não está emprestado (nunca foi
      do pool, ou já devolvido): ``ValueError("objeto não emprestado por este pool")`` (compare por identidade, ``is``). Se ``reset`` levantar uma
      exceção, o objeto é DESCARTADO como acima e a exceção propaga;
    * ``lease(timeout=None)``: gerenciador de contexto (``@contextlib.contextmanager``) que faz ``acquire`` e, no fim, ``release`` (mesmo com exceção);
    * ``stats()``: ``{"created": n, "idle": n, "in_use": n, "discarded": n}``;
    * ``close()``: fecha (``close(obj)``) todos os ociosos; depois disso ``acquire`` levanta ``RuntimeError("pool fechado")`` e ``release`` de um objeto que
      estava emprestado o fecha na hora (em vez de devolvê-lo). Chamar ``close()`` duas vezes não faz mal.
    Deve ser seguro para várias threads (use ``threading.Condition``)."""

    def __init__(self, factory, size: int, *, reset=None, validate=None, close=None):
        raise NotImplementedError

    def acquire(self, timeout: float | None = None):
        raise NotImplementedError

    def release(self, obj) -> None:
        raise NotImplementedError

    def lease(self, timeout: float | None = None):
        raise NotImplementedError

    def stats(self) -> dict:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError
