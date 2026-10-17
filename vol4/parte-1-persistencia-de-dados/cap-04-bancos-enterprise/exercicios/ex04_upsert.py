"""Exercício 4: upsert por dialeto (testado em CADA banco disponível)."""


def upsert_sql(dialect, table, key, columns):
    """Devolve UM comando de upsert para ``table(key, *columns)`` com placeholders ``?``
    (a ordem dos parâmetros é ``key`` e depois ``columns``), usando o ``quote_ident`` do
    exercício 2 na versão do gabarito (reimplemente aspas simples se preferir: os nomes dos
    testes são seguros). Se a chave existe, ATUALIZA as ``columns``; senão INSERE.

    * ``sqlite`` e ``postgresql``: ``INSERT ... ON CONFLICT (key) DO UPDATE SET c = excluded.c``;
    * ``mysql`` e ``mariadb``: ``INSERT ... ON DUPLICATE KEY UPDATE c = VALUES(c)``;
    * ``oracle``: ``MERGE INTO t USING (SELECT ? AS k, ? AS c FROM dual) s ON (t.k = s.k)
      WHEN MATCHED THEN UPDATE SET ... WHEN NOT MATCHED THEN INSERT ...`` (sem ``;`` final);
    * ``mssql``: ``MERGE t AS target USING (SELECT ? AS k, ? AS c) AS s ON target.k = s.k
      WHEN MATCHED THEN UPDATE SET ... WHEN NOT MATCHED THEN INSERT ...;`` (COM ``;`` final);
    * ``columns`` vazio levanta ``ValueError``; dialeto desconhecido também."""
    raise NotImplementedError
