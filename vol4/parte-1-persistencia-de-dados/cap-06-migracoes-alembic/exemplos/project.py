"""Ajuda dos exemplos: monta um projeto Alembic temporário, de forma programática."""
import contextlib
import io
import shutil
import tempfile
import textwrap
from pathlib import Path

from alembic import command
from alembic.config import Config

ENV_PY = '''\
"""env.py mínimo: o metadata e (opcionalmente) a conexão vêm de config.attributes."""
from alembic import context
from sqlalchemy import create_engine, pool

config = context.config
target_metadata = config.attributes.get("target_metadata")


def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"}, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connection = config.attributes.get("connection")
    if connection is None:
        engine = create_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)
        with engine.connect() as connection:
            _run(connection)
    else:
        _run(connection)


def _run(connection):
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True,
                      render_as_batch=connection.dialect.name == "sqlite")
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''


class Project:
    """Um diretório temporário com alembic.ini, migrations/env.py e migrations/versions/."""

    def __init__(self, url, metadata=None):
        self.root = Path(tempfile.mkdtemp(prefix="alembic_demo_"))
        self.config = Config(str(self.root / "alembic.ini"))
        with contextlib.redirect_stdout(io.StringIO()):                 # silencia as mensagens do init
            command.init(self.config, str(self.root / "migrations"))
        (self.root / "migrations" / "env.py").write_text(ENV_PY, encoding="utf-8")
        self.config.set_main_option("script_location", str(self.root / "migrations"))
        self.config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
        self.config.attributes["target_metadata"] = metadata

    @property
    def versions(self):
        return self.root / "migrations" / "versions"

    def revision(self, message, rev_id, autogenerate=True, **kwargs):
        return command.revision(self.config, message=message, autogenerate=autogenerate, rev_id=rev_id, **kwargs)

    def upgrade(self, target="head", sql=False):
        command.upgrade(self.config, target, sql=sql)

    def downgrade(self, target):
        command.downgrade(self.config, target)

    def write_migration(self, rev_id, down_revision, message, upgrade_body, downgrade_body="pass"):
        """Escreve um arquivo de migração à mão (como você faria em uma migração de dados)."""
        text = textwrap.dedent(f'''\
            """{message}

            Revision ID: {rev_id}
            Revises: {down_revision or ""}
            """
            from alembic import op
            import sqlalchemy as sa

            revision = "{rev_id}"
            down_revision = {down_revision!r}
            branch_labels = None
            depends_on = None


            def upgrade():
            {textwrap.indent(textwrap.dedent(upgrade_body), "    ")}


            def downgrade():
            {textwrap.indent(textwrap.dedent(downgrade_body), "    ")}
            ''')
        path = self.versions / f"{rev_id}_{message.replace(' ', '_')}.py"
        path.write_text(text, encoding="utf-8")
        return path

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)
