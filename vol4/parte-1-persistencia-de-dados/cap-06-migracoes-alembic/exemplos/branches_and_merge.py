"""Duas pessoas, duas migrações a partir da mesma base: múltiplas cabeças e o merge."""
import io
import tempfile
from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.script import ScriptDirectory
from alembic.util.exc import CommandError

from project import Project

folder = Path(tempfile.mkdtemp())
url = f"sqlite:///{(folder / 'app.db').as_posix()}"
project = Project(url)

project.write_migration("0001", None, "base", 'op.create_table("person", sa.Column("id", sa.Integer, primary_key=True))', 'op.drop_table("person")')
# Ana e Bia criaram, cada uma na sua branch, uma revisão filha da MESMA base
project.write_migration("aaa1", "0001", "ana adiciona email", 'op.add_column("person", sa.Column("email", sa.String(80)))', 'op.drop_column("person", "email")')
project.write_migration("bbb1", "0001", "bia adiciona telefone", 'op.add_column("person", sa.Column("phone", sa.String(20)))', 'op.drop_column("person", "phone")')


def heads():
    return sorted(ScriptDirectory.from_config(project.config).get_heads())


print("cabeças (heads):", heads(), "<- duas! o histórico ramificou")
try:
    project.upgrade("head")
except CommandError as error:
    print("upgrade head:", str(error).splitlines()[0][:100])

# merge: uma revisão com DOIS pais (não altera o esquema; só junta o histórico)
with __import__("contextlib").redirect_stdout(io.StringIO()):
    command.merge(project.config, ["aaa1", "bbb1"], message="junta as duas branches", rev_id="mmm1")
print("depois do merge, cabeças:", heads())
project.upgrade("head")
engine = sa.create_engine(url)
print("upgrade head aplicou as duas:", [c["name"] for c in sa.inspect(engine).get_columns("person")])

buffer = io.StringIO()
project.config.stdout = buffer
command.history(project.config, indicate_current=False)
print("history:")
for line in buffer.getvalue().strip().splitlines():
    print("  ", line[:100])
print("alternativa: 'alembic upgrade heads' aplica TODAS as cabeças sem merge (mas o histórico continua ramificado)")
engine.dispose()
project.cleanup()
