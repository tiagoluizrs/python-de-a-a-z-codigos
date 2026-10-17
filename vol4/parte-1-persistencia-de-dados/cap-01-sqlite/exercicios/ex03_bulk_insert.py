"""Exercício 3: inserção em lote, atômica e com nomes validados."""
import re  # noqa: F401


def bulk_insert(conn, table, columns, rows, batch_size=1000):
    """Insere ``rows`` (iterável de tuplas) em ``table(columns...)``.

    * ``table`` e cada coluna devem casar com ``^[A-Za-z_][A-Za-z0-9_]*$`` (nomes
      NÃO podem ser parâmetros, então valide); senão ``ValueError`` ANTES de tocar no banco;
    * use ``executemany`` em lotes de ``batch_size`` (``batch_size < 1`` levanta
      ``ValueError``), tudo em UMA transação: se qualquer lote falhar, NADA fica
      inserido e o erro sobe;
    * devolve o número de linhas inseridas (``0`` para ``rows`` vazio);
    * ``rows`` pode ser um gerador: não carregue tudo na memória."""
    raise NotImplementedError
