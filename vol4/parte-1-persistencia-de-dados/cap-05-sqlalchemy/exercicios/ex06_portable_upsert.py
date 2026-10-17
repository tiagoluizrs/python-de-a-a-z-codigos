"""Exercício 6: upsert que funciona em qualquer banco (testado em cada um disponível)."""


def upsert(session, model, values, key):
    """Insere ``values`` (dicionário coluna -> valor, inclui a chave) ou, se já existe uma linha
    com a MESMA ``key`` (nome da coluna), atualiza as outras colunas. NÃO confirma (o chamador faz).

    * ``session.get_bind().dialect.name``: ``sqlite`` e ``postgresql`` usam
      ``on_conflict_do_update`` (``index_elements=[key]``, ``set_`` = demais colunas);
      ``mysql`` e ``mariadb`` usam ``on_duplicate_key_update`` (do dialeto ``mysql``);
    * outros (``oracle``, ``mssql``...): ``SELECT`` pela chave e depois ``UPDATE`` ou ``INSERT``
      na MESMA transação (``session.get`` e atribuição ou ``session.add``);
    * ``key`` fora de ``values`` levanta ``KeyError``."""
    raise NotImplementedError
