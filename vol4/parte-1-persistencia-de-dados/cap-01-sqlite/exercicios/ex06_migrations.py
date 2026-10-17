"""Exercício 6: migrações versionadas com PRAGMA user_version."""


def apply_migrations(conn, migrations):
    """``migrations`` é uma lista de scripts SQL (``executescript``), na ordem. A versão do
    banco fica em ``PRAGMA user_version`` (0 em um banco novo).

    * aplique, em ordem, só as migrações de índice >= versão atual; cada uma em sua
      PRÓPRIA transação junto com a atualização do ``user_version``;
    * se uma falhar: desfaça AQUELA (a versão fica na da última que deu certo) e re-levante;
    * se o banco estiver MAIS NOVO que a lista (``user_version > len(migrations)``),
      levante ``RuntimeError``;
    * devolva a versão final."""
    raise NotImplementedError
