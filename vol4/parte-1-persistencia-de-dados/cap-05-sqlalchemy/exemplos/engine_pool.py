"""Engine e pool: tamanho, espera, pre_ping e o que acontece com conexões mortas."""
import time

import sqlalchemy as sa
from sqlalchemy.pool import NullPool, QueuePool

from dburls import URLS

# 1. QueuePool: pool_size fixas + max_overflow temporárias; esgotou -> espera pool_timeout -> TimeoutError
engine = sa.create_engine("sqlite:///pool_demo.db", poolclass=QueuePool, pool_size=2, max_overflow=1, pool_timeout=0.3)
connections = [engine.connect() for _ in range(3)]               # 2 do pool + 1 de overflow
print("status do pool:", engine.pool.status())
start = time.perf_counter()
try:
    engine.connect()
except Exception as error:
    print(f"4ª conexão: {type(error).__name__} depois de {time.perf_counter() - start:.2f} s (o pool esgotou)")
for connection in connections:
    connection.close()
engine.dispose()

# 2. NullPool: sem pool (cada connect() abre uma conexão nova): testes, funções serverless, após fork
tiny = sa.create_engine("sqlite://", poolclass=NullPool)
print("NullPool:", type(tiny.pool).__name__)

# 3. pool_pre_ping: testa a conexão antes de entregar (recupera de conexões derrubadas)
try:
    pg = sa.create_engine(URLS["postgresql"], pool_size=1, max_overflow=0, pool_pre_ping=True)
    with pg.connect() as conn:
        pid = conn.execute(sa.text("SELECT pg_backend_pid()")).scalar()
    with sa.create_engine(URLS["postgresql"], poolclass=NullPool).connect() as admin:
        admin.execute(sa.text("SELECT pg_terminate_backend(:pid)"), {"pid": pid})
        admin.commit()
    time.sleep(0.2)
    with pg.connect() as conn:                                   # a conexão do pool estava morta: o pre_ping a substituiu
        print("pool_pre_ping: a conexão derrubada foi trocada sem erro; novo backend:", conn.execute(sa.text("SELECT pg_backend_pid()")).scalar() != pid)
    pg.dispose()
    broken = sa.create_engine(URLS["postgresql"], pool_size=1, max_overflow=0, pool_pre_ping=False)
    with broken.connect() as conn:
        pid = conn.execute(sa.text("SELECT pg_backend_pid()")).scalar()
    with sa.create_engine(URLS["postgresql"], poolclass=NullPool).connect() as admin:
        admin.execute(sa.text("SELECT pg_terminate_backend(:pid)"), {"pid": pid})
        admin.commit()
    time.sleep(0.2)
    try:
        with broken.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
    except sa.exc.OperationalError as error:
        print("sem pre_ping: OperationalError na primeira consulta depois da queda:", type(error.orig).__name__)
    broken.dispose()
except sa.exc.OperationalError:
    print("(PostgreSQL indisponível: pule a demonstração do pool_pre_ping)")

import os
for leftover in ("pool_demo.db",):
    if os.path.exists(leftover):
        os.remove(leftover)
print("Em produção: pool_size ~ conexões simultâneas, pool_pre_ping=True, pool_recycle < timeout do banco/firewall; após fork (Cap. 16 do Volume 3) chame engine.dispose().")
