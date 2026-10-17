"""SQLite e ALTER: o que ele faz direto e quando o 'batch mode' (recriar a tabela) é preciso."""
import sqlite3

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

print("SQLite embutido:", sqlite3.sqlite_version)
engine = sa.create_engine("sqlite://", poolclass=sa.pool.StaticPool)
statements = []
sa.event.listen(engine, "before_cursor_execute", lambda conn, cur, stmt, *rest: statements.append(" ".join(stmt.split())))


def column(conn, name):
    return next(c for c in sa.inspect(conn).get_columns("person") if c["name"] == name)


with engine.begin() as conn:
    conn.execute(sa.text("CREATE TABLE person (id INTEGER PRIMARY KEY, name VARCHAR(50), age INTEGER)"))
    conn.execute(sa.text("INSERT INTO person (name, age) VALUES ('ana', 30), ('bia', NULL)"))
    operations = Operations(MigrationContext.configure(conn))

    # 1. NOT NULL direto: o SQLite 3.53+ já tem ALTER COLUMN ... SET NOT NULL (versões antigas não tinham)
    statements.clear()
    operations.alter_column("person", "name", nullable=False)
    print("1) alter_column(nullable=False):", statements, "->", "NOT NULL" if not column(conn, "name")["nullable"] else "NULL-ável")

    # 2. mudar o TIPO: continua não existindo no SQLite
    try:
        operations.alter_column("person", "age", type_=sa.String(10))
    except Exception as error:
        print("2) alter_column(type_=...):", type(error).__name__, "- o SQLite não muda o tipo de uma coluna")

    # 3. batch mode: Alembic cria a tabela nova, copia os dados, apaga a antiga e renomeia
    statements.clear()
    with operations.batch_alter_table("person", recreate="always") as batch:
        batch.alter_column("age", existing_type=sa.Integer, type_=sa.String(10))
    print("3) batch_alter_table emitiu:")
    for statement in [s for s in statements if not s.startswith(("PRAGMA", "SELECT sql"))]:
        print("  ", statement[:112])
    print("   dados preservados:", conn.execute(sa.text("SELECT name, age FROM person ORDER BY id")).fetchall())
    print("   tipo agora:", column(conn, "age")["type"])
print("Dica: o env.py com render_as_batch=True (visto em project.py) faz o --autogenerate gerar batch_alter_table sozinho no SQLite.")
