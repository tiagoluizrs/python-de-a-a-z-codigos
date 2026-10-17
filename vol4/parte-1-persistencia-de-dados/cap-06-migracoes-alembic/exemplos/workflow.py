"""O fluxo completo: modelo -> revisão automática -> upgrade -> mudança no modelo -> nova revisão -> downgrade."""
import contextlib
import io
import tempfile
from pathlib import Path

import sqlalchemy as sa
from alembic import command
from sqlalchemy import ForeignKey, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from project import Project

# nomes determinísticos para as restrições (essencial para poder alterá-las/removê-las depois)
CONVENTION = {"ix": "ix_%(column_0_label)s", "uq": "uq_%(table_name)s_%(column_0_name)s",
              "ck": "ck_%(table_name)s_%(constraint_name)s", "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
              "pk": "pk_%(table_name)s"}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENTION)


class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


folder = Path(tempfile.mkdtemp())
url = f"sqlite:///{(folder / 'app.db').as_posix()}"
project = Project(url, Base.metadata)
engine = sa.create_engine(url)


def show(title):
    insp = sa.inspect(engine)
    print(f"{title}: tabelas {sorted(insp.get_table_names())}", {t: [c['name'] for c in insp.get_columns(t)] for t in sorted(insp.get_table_names()) if t != 'alembic_version'})


with contextlib.redirect_stdout(io.StringIO()):
    project.revision("cria autor", "0001")                      # compara o modelo com o banco (vazio) e GERA o script
print("1) script gerado:", sorted(p.name for p in project.versions.glob("*.py")))
print("   conteúdo do upgrade():")
for line in (project.versions / "0001_cria_autor.py").read_text().split("def upgrade")[1].split("def downgrade")[0].splitlines()[1:8]:
    print("    ", line)
project.upgrade()
show("2) depois do upgrade head")
with engine.connect() as conn:
    print("   alembic_version:", conn.execute(sa.text("SELECT version_num FROM alembic_version")).scalar())

# o modelo evolui: nova coluna e nova tabela
class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(80))
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))


Author.born = mapped_column(sa.Integer, nullable=True)
with contextlib.redirect_stdout(io.StringIO()):
    project.revision("adiciona livro e nascimento", "0002")
body = (project.versions / "0002_adiciona_livro_e_nascimento.py").read_text().split("def upgrade")[1].split("def downgrade")[0]
print("3) a 2ª revisão detectou só a DIFERENÇA:", [l.strip()[:60] for l in body.splitlines() if "op." in l])
project.upgrade()
show("4) depois do 2º upgrade")
project.downgrade("0001")
show("5) depois do downgrade -1")
project.upgrade()

# modo offline: o SQL da migração, sem tocar no banco (para o DBA revisar)
buffer = io.StringIO()
project.config.output_buffer = buffer
command.upgrade(project.config, "0001:0002", sql=True)
print("6) --sql (offline) de 0001 -> 0002:")
for line in [l for l in buffer.getvalue().splitlines() if l.strip() and not l.startswith("--")][:6]:
    print("    ", line)
engine.dispose()
project.cleanup()
