"""Exercício 2: repositório sobre PyMySQL (sem RETURNING: funciona no MySQL E no MariaDB)."""


class ProductRepository:
    """``ProductRepository(conn)`` (PyMySQL com ``DictCursor``, autocommit DESLIGADO).

    * ``create_schema()``: ``product(id INT AUTO_INCREMENT PRIMARY KEY, sku VARCHAR(20) NOT NULL
      COLLATE utf8mb4_bin, name VARCHAR(60) NOT NULL, stock INT NOT NULL DEFAULT 0,
      UNIQUE KEY uq_sku (sku)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`; confirma;
    * ``add(sku, name, stock=0)`` -> dicionário da linha (use ``lastrowid`` e um ``SELECT``);
      SKU repetido (a coluna é sensível a maiúsculas) levanta ``ValueError`` e a conexão
      continua utilizável;
    * ``get(id)`` -> dicionário ou ``None``;
    * ``add_stock(sku, quantity)``: soma ``quantity`` (pode ser negativo) ao estoque; se o
      SKU não existir levanta ``KeyError``; se o estoque ficasse negativo levanta
      ``ValueError`` e NADA muda;
    * ``upsert(sku, name, stock)``: insere ou, se o SKU existir, atualiza ``name`` e SOMA
      ``stock`` (``ON DUPLICATE KEY UPDATE``); devolve ``True`` se inseriu, ``False`` se atualizou
      (dica: ``cursor.rowcount`` vale 1 ao inserir e 2 ao atualizar uma linha alterada);
    * toda escrita é confirmada."""

    def __init__(self, conn):
        raise NotImplementedError
