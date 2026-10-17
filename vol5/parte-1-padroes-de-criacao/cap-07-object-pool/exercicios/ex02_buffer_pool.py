"""Exercício 2: um pool de buffers (``bytearray``) para copiar fluxos sem alocar um bloco novo a cada leitura."""


class BufferPool:
    """``BufferPool(buffer_size, count)``: cria ``count`` ``bytearray`` de ``buffer_size`` bytes (ambos ``>= 1``, senão ``ValueError``).

    * ``acquire()``: devolve um buffer livre (o mesmo objeto, não uma cópia); sem nenhum livre: ``BufferError("sem buffers livres")``;
    * ``release(buf)``: devolve; um buffer que não é deste pool, ou que já foi devolvido: ``ValueError("buffer desconhecido")`` (compare por identidade);
    * ``free``: quantos buffers estão livres agora."""

    def __init__(self, buffer_size: int, count: int):
        raise NotImplementedError

    def acquire(self) -> bytearray:
        raise NotImplementedError

    def release(self, buf: bytearray) -> None:
        raise NotImplementedError

    @property
    def free(self) -> int:
        raise NotImplementedError


def copy_stream(src, dst, pool: BufferPool) -> int:
    """Copia ``src`` para ``dst`` (objetos de arquivo binários) usando UM buffer do pool: ``src.readinto(buf)`` e ``dst.write(memoryview(buf)[:n])``,
    até ``readinto`` devolver 0. Devolve o total de bytes copiados. O buffer VOLTA ao pool sempre, mesmo se ``dst.write`` levantar uma exceção
    (que deve propagar)."""
    raise NotImplementedError
