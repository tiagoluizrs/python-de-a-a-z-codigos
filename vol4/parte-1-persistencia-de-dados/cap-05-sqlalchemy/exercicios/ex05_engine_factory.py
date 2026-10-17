"""Exercício 5: uma fábrica de engines com padrões sensatos por banco."""


def make_engine(url, *, echo=False, pool_size=5, max_overflow=10):
    """Cria o ``Engine`` com o pool certo para o banco da ``url``:

    * esquema ``sqlite`` em MEMÓRIA (``sqlite://`` ou ``sqlite:///:memory:``): ``StaticPool`` e
      ``connect_args={"check_same_thread": False}`` (uma única conexão compartilhada);
    * ``sqlite`` em ARQUIVO: ``NullPool`` (sem pool);
    * qualquer banco: no evento ``connect`` do SQLite, execute ``PRAGMA foreign_keys = ON``;
    * outros bancos (``postgresql``, ``mysql``, ``mariadb``, ``oracle``, ``mssql``, com ou sem
      ``+driver``): ``QueuePool`` com ``pool_size``, ``max_overflow``, ``pool_pre_ping=True`` e
      ``pool_recycle=1800``;
    * esquema vazio ou desconhecido (``mongodb://``) levanta ``ValueError``;
    * ``pool_size < 1`` ou ``max_overflow < 0`` levantam ``ValueError`` (nos bancos com pool)."""
    raise NotImplementedError
