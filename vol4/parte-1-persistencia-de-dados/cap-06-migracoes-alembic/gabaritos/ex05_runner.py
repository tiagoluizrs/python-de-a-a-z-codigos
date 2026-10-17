"""Gabarito do exercício 5."""
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory


def current_revision(engine):
    with engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()


def pending_revisions(config, engine):
    script = ScriptDirectory.from_config(config)
    if len(script.get_heads()) > 1:
        raise RuntimeError("múltiplas cabeças")
    current = current_revision(engine)
    revisions = [r.revision for r in script.iterate_revisions("head", current if current else "base")]
    revisions.reverse()
    return [r for r in revisions if r != current]
