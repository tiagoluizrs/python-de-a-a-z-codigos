"""Exercício 2: convenção de nomes para restrições (essencial para migrar com segurança)."""


def build_shop_metadata():
    """Devolve um ``MetaData`` com ``naming_convention`` e duas tabelas.

    Convenção (chaves ``ix``, ``uq``, ``ck``, ``fk``, ``pk``):
    ``ix_%(column_0_label)s``, ``uq_%(table_name)s_%(column_0_name)s``,
    ``ck_%(table_name)s_%(constraint_name)s``,
    ``fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s``, ``pk_%(table_name)s``.

    Tabelas (``sqlalchemy.Table``, Core):

    * ``customer``: ``id`` Integer PK; ``name`` String(60) não nulo COM ÍNDICE (``index=True``);
      ``email`` String(120) não nulo ÚNICO;
    * ``orders``: ``id`` Integer PK; ``customer_id`` Integer não nulo FK para ``customer.id``;
      ``total`` Numeric(10, 2) não nulo; ``CheckConstraint("total >= 0", name="total_non_negative")``."""
    raise NotImplementedError


def constraint_names(metadata):
    """Conjunto com os NOMES de todas as restrições nomeadas e índices de todas as tabelas de
    ``metadata`` (chaves primárias, únicas, estrangeiras, ``CHECK`` e índices), sem ``None``."""
    raise NotImplementedError
