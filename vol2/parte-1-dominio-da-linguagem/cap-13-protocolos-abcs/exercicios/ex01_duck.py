"""Exercício 1: funções que funcionam com qualquer objeto "parecido"."""


def copy_stream(source, target, chunk_size=4):
    """Copie ``source`` para ``target`` em blocos e devolva o total copiado.

    ``source`` é qualquer objeto com ``read(n)``; ``target``, qualquer objeto
    com ``write(dados)``. Pare quando ``read`` devolver vazio (``""`` ou
    ``b""``). Não verifique tipos: use duck typing. Não use ``isinstance``.
    """
    raise NotImplementedError


def quack_all(items, method="speak"):
    """Chame ``item.<method>()`` em cada item e devolva a lista de resultados.

    Itens SEM o método devem ser ignorados (EAFP: ``try/except
    AttributeError``), mas um ``AttributeError`` levantado DENTRO do método
    deve se propagar (cuidado: só proteja o ACESSO ao método).
    """
    raise NotImplementedError
