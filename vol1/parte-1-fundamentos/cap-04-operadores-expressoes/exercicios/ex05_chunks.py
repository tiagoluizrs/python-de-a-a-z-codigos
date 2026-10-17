"""Exercício 5: o operador morsa (:=) em um laço de leitura."""
import io


def read_in_chunks(stream: io.BufferedIOBase, size: int) -> list[bytes]:
    """Leia ``stream`` em blocos de ``size`` bytes e devolva a lista de blocos.

    Use o operador ``:=`` no ``while``. O último bloco pode ser menor.
    Exemplo: BytesIO(b'abcdefghij'), 4 -> [b'abcd', b'efgh', b'ij']
    """
    raise NotImplementedError
