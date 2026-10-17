"""Migração de dados em três passos (expandir -> preencher -> contrair), sem bloquear por muito tempo."""
import time
import uuid

import sqlalchemy as sa

from dburls import available_engines

N = 400_000
engines = available_engines()
engine = engines.get("postgresql") or engines["sqlite"]
name = "postgresql" if "postgresql" in engines else "sqlite"
table_name = "mig_user_" + uuid.uuid4().hex[:6]
print(f"banco: {name} | tabela com {N:,} linhas")

# lightweight table(): a migração NÃO importa os modelos da aplicação (eles mudam; a migração é fixa no tempo)
users = sa.table(table_name, sa.column("id", sa.Integer), sa.column("email", sa.String), sa.column("domain", sa.String))

with engine.begin() as conn:
    conn.execute(sa.text(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, email VARCHAR(80) NOT NULL)"))
    conn.execute(sa.text(f"INSERT INTO {table_name} (id, email) VALUES (:id, :email)"), [{"id": i, "email": f"user{i}@empresa{i % 50}.com"} for i in range(N)])


def step(label, fn):
    start = time.perf_counter()
    result = fn()
    print(f"  {label:<62} {(time.perf_counter() - start) * 1e3:9.1f} ms")
    return result


print("passo 1 - EXPANDIR: adicionar a coluna como NULL-ável (rápido, compatível com o código antigo):")


def add_column():
    with engine.begin() as conn:
        conn.execute(sa.text(f"ALTER TABLE {table_name} ADD COLUMN domain VARCHAR(80)"))


step("ALTER TABLE ... ADD COLUMN domain VARCHAR(80) NULL", add_column)

print("passo 2 - PREENCHER: um UPDATE gigante contra lotes pequenos (cada lote = uma transação curta):")
expr = sa.func.substr(users.c.email, sa.func.instr(users.c.email, "@") + 1) if name == "sqlite" else sa.func.split_part(users.c.email, "@", 2)


def single_update():
    with engine.begin() as conn:
        conn.execute(users.update().values(domain=expr))


def batched_update(batch=20_000):
    longest = 0.0
    for low in range(0, N, batch):
        start = time.perf_counter()
        with engine.begin() as conn:
            conn.execute(users.update().where(users.c.id >= low, users.c.id < low + batch, users.c.domain.is_(None)).values(domain=expr))
        longest = max(longest, time.perf_counter() - start)
    return longest


step("UPDATE de uma vez (UMA transação longa: trava as linhas todas)", single_update)
with engine.begin() as conn:
    conn.execute(users.update().values(domain=None))
start = time.perf_counter()
longest = batched_update()
print(f"  {'UPDATE em lotes de 20.000 (20 transações)':<62} {(time.perf_counter() - start) * 1e3:9.1f} ms | MAIOR transação: {longest * 1e3:.1f} ms")
print("  (o tempo total é parecido ou maior; o ganho é o TEMPO QUE CADA TRAVA DURA: outros escritores esperam ms, não segundos)")

print("passo 3 - CONTRAIR: agora que não há NULL, exigir NOT NULL (e só então remover o código antigo):")
with engine.begin() as conn:
    nulls = conn.execute(sa.select(sa.func.count()).select_from(users).where(users.c.domain.is_(None))).scalar_one()
    print(f"  linhas ainda NULL: {nulls}  ->", end=" ")
    if name == "sqlite":
        print("(no SQLite, ALTER COLUMN exige batch_alter_table: veja sqlite_batch.py)")
    else:
        conn.execute(sa.text(f"ALTER TABLE {table_name} ALTER COLUMN domain SET NOT NULL"))
        print("SET NOT NULL aplicado")
    print("  amostra:", conn.execute(sa.select(users.c.email, users.c.domain).limit(2)).all())
    conn.execute(sa.text(f"DROP TABLE {table_name}"))
for e in engines.values():
    e.dispose()
