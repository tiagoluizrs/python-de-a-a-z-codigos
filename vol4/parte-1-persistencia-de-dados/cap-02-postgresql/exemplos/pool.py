"""Pool de conexões: por que existe, quanto custa, como dimensionar."""
import threading
import time

import psycopg
from psycopg_pool import ConnectionPool, PoolTimeout

from pgenv import DSN

start = time.perf_counter()
for _ in range(20):
    psycopg.connect(DSN).close()
connect_cost = (time.perf_counter() - start) / 20
print(f"abrir e fechar uma conexão: {connect_cost * 1e3:.1f} ms (autenticação, memória do servidor)")

with ConnectionPool(DSN, min_size=2, max_size=5) as pool:
    pool.wait()
    start = time.perf_counter()
    for _ in range(2000):
        with pool.connection():
            pass
    checkout = (time.perf_counter() - start) / 2000
    print(f"emprestar uma conexão do pool: {checkout * 1e6:.1f} us ({connect_cost / checkout:,.0f}x mais barato)")

    # o pool limita a concorrência: 10 tarefas de 0,2 s com max_size=5 levam 2 rodadas
    def work():
        with pool.connection() as conn:
            conn.execute("SELECT pg_sleep(0.2)")

    start = time.perf_counter()
    threads = [threading.Thread(target=work) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"10 consultas de 0,2 s, pool max_size=5: {time.perf_counter() - start:.2f} s (2 rodadas de 5)")
    stats = pool.get_stats()
    print("estatísticas:", {k: stats[k] for k in ("pool_min", "pool_max", "pool_size", "requests_num", "requests_waiting", "usage_ms")})

# esgotado: quem espera mais que o timeout recebe PoolTimeout
with ConnectionPool(DSN, min_size=1, max_size=1, timeout=0.3) as tiny:
    tiny.wait()
    with tiny.connection():
        try:
            with tiny.connection():
                pass
        except PoolTimeout as error:
            print("pool de 1 conexão esgotado ->", type(error).__name__)

# dimensionamento (lei de Little, Capítulo 14 do Volume 3): conexões = chegadas/s x tempo de serviço
rps, service = 200, 0.020
print(f"{rps} req/s x {service * 1e3:.0f} ms por consulta = {rps * service:.0f} conexões ocupadas em média (some folga; o PostgreSQL tem um teto: max_connections)")
