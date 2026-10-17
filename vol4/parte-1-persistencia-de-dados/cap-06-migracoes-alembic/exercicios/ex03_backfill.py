"""Exercício 3: migração de dados em passos pequenos."""
import re  # noqa: F401


def plan_add_required_column(table, column, column_type, fill_expression):
    """Planeja a adição de uma coluna OBRIGATÓRIA em uma tabela com dados, sem bloquear por muito
    tempo (padrão expandir -> preencher -> contrair). Devolve a lista de 3 passos (textos):

    1. ``ALTER TABLE <table> ADD COLUMN <column> <column_type> NULL``
    2. ``UPDATE <table> SET <column> = <fill_expression> WHERE <column> IS NULL`` (a ser executado em lotes)
    3. ``ALTER TABLE <table> ALTER COLUMN <column> SET NOT NULL``

    ``table`` e ``column`` devem casar com ``^[A-Za-z_][A-Za-z0-9_]*$`` (``ValueError``);
    ``fill_expression`` e ``column_type`` são SQL escrito por você (não validar)."""
    raise NotImplementedError


def backfill(conn, table, column, value, batch_size=1000, id_column="id"):
    """Preenche ``column = value`` onde ela é ``NULL``, em lotes por faixa de ``id_column``
    (``WHERE id >= low AND id < low + batch_size AND column IS NULL``), UMA transação curta por
    lote (``conn.commit()`` depois de cada lote). ``conn`` é uma conexão SQLAlchemy 2.x já
    aberta (``autobegin``). Devolve a quantidade de lotes que EXECUTARAM (``id_column`` de ``0``
    até o maior id). Rodar de novo não altera nada. ``batch_size < 1`` e nomes inválidos levantam
    ``ValueError``; tabela vazia devolve ``0``. ``value`` vai como parâmetro."""
    raise NotImplementedError
