"""Exercício 4: detectar deriva entre o modelo e o banco migrado."""


class DriftError(AssertionError):
    """O banco não corresponde ao ``MetaData`` (``.differences`` guarda a lista de textos)."""

    def __init__(self, differences):
        super().__init__("deriva entre modelo e banco: " + "; ".join(differences))
        self.differences = differences


def schema_drift(engine, metadata):
    """Compara o banco com ``metadata`` usando ``alembic.autogenerate.compare_metadata``
    (``MigrationContext.configure(conn, opts={"compare_type": True})``) e devolve uma lista ORDENADA
    de textos: ``"add_table:<tabela>"``, ``"remove_table:<tabela>"``, ``"add_column:<tabela>.<coluna>"``,
    ``"remove_column:<tabela>.<coluna>"``, ``"modify_type:<tabela>.<coluna>"``,
    ``"modify_nullable:<tabela>.<coluna>"`` (ignore o que não conhecer). A tabela
    ``alembic_version`` NÃO conta. Lista vazia = em sincronia."""
    raise NotImplementedError


def assert_in_sync(engine, metadata):
    """Levanta ``DriftError`` (com as diferenças) se houver deriva; senão devolve ``None``."""
    raise NotImplementedError
