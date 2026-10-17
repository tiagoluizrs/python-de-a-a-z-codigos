"""Exercício 5: consultar o estado das migrações por código."""


def current_revision(engine):
    """Revisão atual do banco (``MigrationContext.get_current_revision()``) ou ``None`` se o banco
    nunca foi migrado."""
    raise NotImplementedError


def pending_revisions(config, engine):
    """Lista, na ORDEM DE APLICAÇÃO, dos ids das revisões que um ``upgrade head`` aplicaria agora
    (use ``ScriptDirectory.from_config(config)`` e ``iterate_revisions("head", atual)``; lembre
    que a iteração vai da cabeça para trás). Banco em dia devolve ``[]``; com várias cabeças
    levante ``RuntimeError("múltiplas cabeças")`` (``len(script.get_heads()) > 1``)."""
    raise NotImplementedError
