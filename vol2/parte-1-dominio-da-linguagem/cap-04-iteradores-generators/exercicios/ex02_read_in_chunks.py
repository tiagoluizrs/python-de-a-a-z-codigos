"""Exercício 2: ler em blocos com um gerador.

Implemente ``read_in_chunks(stream, size)``: gerador que lê de um objeto
com ``.read(n)`` (arquivo aberto, ``io.BytesIO``, ``io.StringIO``) e
entrega blocos de até ``size`` unidades, até o fim (``read`` devolve
vazio). ``size`` menor que 1 levanta ``ValueError`` ao consumir.

Implemente também ``count_bytes(stream, size=4096)`` que soma o tamanho
dos blocos usando ``read_in_chunks``.

Dica: ``while chunk := stream.read(size): yield chunk``.

Exemplo: ``list(read_in_chunks(io.BytesIO(b"abcde"), 2))``
         ``== [b"ab", b"cd", b"e"]``
"""


def read_in_chunks(stream, size=4096):
    raise NotImplementedError


def count_bytes(stream, size=4096):
    raise NotImplementedError
