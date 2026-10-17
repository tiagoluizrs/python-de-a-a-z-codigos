"""Testar migrações: vai-e-volta, e 'o modelo bate com as migrações?' (detecção de deriva)."""
import tempfile
from pathlib import Path

import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from project import Project


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={"pk": "pk_%(table_name)s", "uq": "uq_%(table_name)s_%(column_0_name)s"})


class Person(Base):
    __tablename__ = "person"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


folder = Path(tempfile.mkdtemp())
url = f"sqlite:///{(folder / 'app.db').as_posix()}"
project = Project(url, Base.metadata)
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    project.revision("cria pessoa", "0001")
engine = sa.create_engine(url)


def tables():
    return sorted(t for t in sa.inspect(engine).get_table_names() if t != "alembic_version")


# teste 1: upgrade -> downgrade -> upgrade (as migrações são reversíveis e repetíveis)
project.upgrade()
print("1) upgrade head          ->", tables())
project.downgrade("base")
print("   downgrade base        ->", tables())
project.upgrade()
print("   upgrade head de novo  ->", tables())


# teste 2: o esquema do banco migrado é IGUAL ao dos modelos? (detecta quem mudou o modelo e esqueceu a migração)
def drift():
    with engine.connect() as conn:
        return compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), Base.metadata)


print("2) deriva (modelo x banco):", drift() or "nenhuma")
Person.__table__.append_column(sa.Column("email", String(80)))               # alguém muda o modelo e esquece a migração
changes = drift()
print("   depois de mudar o modelo SEM migração:", [(c[0], c[3].name) if c[0] == "add_column" else c[0] for c in changes], "<- o teste falha aqui")
print("   em CI: assert not drift()  ->  'o modelo mudou; gere a migração com alembic revision --autogenerate'")
engine.dispose()
project.cleanup()
