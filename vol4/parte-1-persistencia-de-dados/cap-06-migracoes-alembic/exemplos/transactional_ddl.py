"""O DDL é transacional? Uma migração que falha no meio, em cada banco."""
import uuid

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from dburls import available_engines


def failing_migration(op, a, b):
    op.create_table(a, sa.Column("id", sa.Integer, primary_key=True))
    op.create_table(b, sa.Column("id", sa.Integer, primary_key=True))
    op.create_table(a, sa.Column("id", sa.Integer, primary_key=True))        # erro: a tabela já existe


print(f"{'banco':<12}{'o Alembic trata o DDL como transacional?':<44}{'depois da falha, sobraram':<28}")
for name, engine in available_engines().items():
    a, b = "mig_a_" + uuid.uuid4().hex[:8], "mig_b_" + uuid.uuid4().hex[:8]
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        transactional = context.impl.transactional_ddl
        operations = Operations(context)
        try:
            with context.begin_transaction():
                failing_migration(operations, a, b)
        except Exception:
            pass
        try:
            conn.rollback()
        except Exception:
            pass
    inspector = sa.inspect(engine)
    left = sorted(t for t in (a, b) if inspector.has_table(t))                                       # has_table: funciona também com o usuário SYSTEM do Oracle
    print(f"{name:<12}{str(transactional):<44}{(', '.join(t[:5] for t in left) or 'nenhuma tabela (tudo desfeito)'):<28}")
    with engine.begin() as conn:
        for table in (a, b):
            if table in left:
                conn.execute(sa.text(f"DROP TABLE {table}"))
    engine.dispose()
print("\nLeitura: onde o DDL NÃO é transacional, uma migração com vários comandos que falha no meio deixa o banco")
print("PELA METADE, e o 'alembic_version' continua na revisão anterior. Escreva migrações PEQUENAS (um passo por revisão).")
