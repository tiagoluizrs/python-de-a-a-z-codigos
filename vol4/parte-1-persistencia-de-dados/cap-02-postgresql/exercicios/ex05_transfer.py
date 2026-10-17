"""Exercício 5: transferência sem deadlock."""


def transfer(conn, source_id, target_id, amount):
    """Tabela ``account(id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0))``.

    Dentro de ``conn.transaction()``: trave AS DUAS contas com
    ``SELECT ... WHERE id IN (...) ORDER BY id FOR UPDATE`` (sempre em ordem de ``id``),
    verifique, e mova ``amount``.

    * ``source_id == target_id``, ``amount <= 0``, conta inexistente ou saldo
      insuficiente levantam ``ValueError`` (e nada muda);
    * duas transferências em sentidos opostos, ao mesmo tempo, NÃO podem dar deadlock;
    * ``conn`` usa ``autocommit=False`` e ``row_factory=dict_row``; confirme no fim."""
    raise NotImplementedError
