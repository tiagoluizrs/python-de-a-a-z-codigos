"""Ler planos de execução: varreduras, junções, estatísticas desatualizadas (PostgreSQL)."""
from lab import lab


def explain(conn, sql, params=None, analyze=True):
    options = "ANALYZE, COSTS, TIMING OFF" if analyze else "COSTS"
    return [row[0] for row in conn.execute(f"EXPLAIN ({options}) " + sql, params)]


with lab() as conn:
    conn.execute("CREATE TABLE customer (id int PRIMARY KEY, name text)")
    conn.execute("CREATE TABLE sale (id serial PRIMARY KEY, customer_id int, amount numeric)")
    conn.execute("INSERT INTO customer SELECT g, 'c' || g FROM generate_series(1, 10000) g")
    conn.execute("INSERT INTO sale (customer_id, amount) SELECT (g % 10000) + 1, g FROM generate_series(1, 200000) g")
    conn.execute("ANALYZE")

    print("1) um plano, linha a linha (EXPLAIN ANALYZE):")
    for line in explain(conn, "SELECT c.name, sum(s.amount) FROM customer c JOIN sale s ON s.customer_id = c.id WHERE c.id < 100 GROUP BY c.name"):
        print("  ", line.rstrip()[:120])
    print("   cost=A..B  : custo ESTIMADO (início..total) em unidades abstratas | rows= : linhas ESTIMADAS | actual rows= : linhas REAIS")
    print("   Compare 'rows' com 'actual rows': uma diferença enorme é a causa nº 1 de planos ruins (estatísticas velhas).")

    print("\n2) os algoritmos de junção (forçados para comparar):")
    query = "SELECT count(*) FROM customer c JOIN sale s ON s.customer_id = c.id"
    for label, setting in (("Hash Join (o padrão para esta consulta)", "SET enable_nestloop = on"),
                           ("Nested Loop (sem hash e sem merge)", "SET enable_hashjoin = off; SET enable_mergejoin = off"),
                           ("Merge Join (sem hash e sem nested loop)", "SET enable_hashjoin = off; SET enable_nestloop = off")):
        for flag in ("enable_nestloop", "enable_hashjoin", "enable_mergejoin"):
            conn.execute(f"SET {flag} = on")
        for statement in setting.split("; "):
            conn.execute(statement)
        lines = explain(conn, query)
        join = next(line.strip().split("  (")[0].replace("->", "").strip() for line in lines if "Join" in line or "Nested Loop" in line)
        total = float(lines[-1].split(":")[1].split("ms")[0]) if "Execution Time" in lines[-1] else float("nan")
        print(f"   {label:<42} -> {join:<14} {total:8.1f} ms")
    for flag in ("enable_nestloop", "enable_hashjoin", "enable_mergejoin"):
        conn.execute(f"SET {flag} = on")
    print("   Hash Join: constrói uma tabela hash da menor e varre a maior (bom para grandes volumes sem índice)")
    print("   Nested Loop: para cada linha da externa, procura na interna (ótimo com poucas linhas e índice)")
    print("   Merge Join: duas entradas ordenadas (bom quando já vêm ordenadas por índice)")

    print("\n3) ESTATÍSTICAS desatualizadas enganam o planejador:")
    conn.execute("CREATE TABLE fresh (id serial PRIMARY KEY, flag int)")
    conn.execute("CREATE INDEX ON fresh (flag)")
    conn.execute("ALTER TABLE fresh SET (autovacuum_enabled = false)")
    conn.execute("INSERT INTO fresh (flag) SELECT 0 FROM generate_series(1, 5)")
    conn.execute("ANALYZE fresh")                                      # o banco 'aprende' que a tabela tem 5 linhas
    conn.execute("INSERT INTO fresh (flag) SELECT 1 FROM generate_series(1, 300000)")   # e agora tem 300.005
    stale = explain(conn, "SELECT * FROM fresh WHERE flag = 1")
    estimate = next(line for line in stale if "Scan" in line)
    print("   antes do ANALYZE :", estimate.strip()[:105])
    conn.execute("ANALYZE fresh")
    updated = explain(conn, "SELECT * FROM fresh WHERE flag = 1")
    print("   depois do ANALYZE:", next(line for line in updated if "Scan" in line).strip()[:105])
    print("   O autovacuum faz ANALYZE sozinho, mas depois de uma carga grande rode ANALYZE (e confira rows= contra actual rows=).")
