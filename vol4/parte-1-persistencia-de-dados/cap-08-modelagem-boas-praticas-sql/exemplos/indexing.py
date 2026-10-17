"""Estratégia de índices medida: composto, cobertura, expressão, sargabilidade, LIKE, custo (PostgreSQL)."""
from lab import lab, plan, timed

with lab() as conn:
    conn.execute("CREATE TABLE ev (id bigserial PRIMARY KEY, a int, b int, email text, created timestamptz, payload text)")
    conn.execute("""INSERT INTO ev (a, b, email, created, payload)
        SELECT g % 1000, g % 50, 'User' || g || '@X.com', now() - (g || ' minutes')::interval, md5(g::text) FROM generate_series(1, 1000000) g""")
    conn.execute("ANALYZE ev")
    print("tabela com 1.000.000 de linhas\n")

    def show(label, sql, params=None):
        node, ms = plan(conn, sql, params)
        print(f"  {label:<58}{node:<20}{ms:>9.2f} ms")

    print("1) índice COMPOSTO (a, b): a ordem das colunas importa (prefixo à esquerda)")
    show("sem índice: WHERE a = 5", "SELECT * FROM ev WHERE a = 5")
    conn.execute("CREATE INDEX ev_ab ON ev (a, b)")
    conn.execute("ANALYZE ev")
    show("com (a, b): WHERE a = 5", "SELECT * FROM ev WHERE a = 5")
    show("com (a, b): WHERE a = 5 AND b = 5", "SELECT * FROM ev WHERE a = 5 AND b = 5")
    show("com (a, b): WHERE b = 5  (SÓ a 2ª coluna)", "SELECT * FROM ev WHERE b = 5")
    print("     -> o índice (a, b) serve a consultas por 'a' e por 'a e b', mas NÃO por 'b' sozinha.")

    print("\n2) EXPRESSÃO e SARGABILIDADE: não esconda a coluna indexada atrás de uma função")
    show("WHERE lower(email) = ... (sem índice na expressão)", "SELECT * FROM ev WHERE lower(email) = %s", ("user500@x.com",))
    conn.execute("CREATE INDEX ev_lower ON ev (lower(email))")
    show("com índice em lower(email)", "SELECT * FROM ev WHERE lower(email) = %s", ("user500@x.com",))
    conn.execute("CREATE INDEX ev_created ON ev (created)")
    conn.execute("ANALYZE ev")
    show("WHERE created::date = ... (função na coluna: NÃO sargável)", "SELECT * FROM ev WHERE created::date = current_date - 5")
    show("WHERE created >= ... AND created < ... (faixa: sargável)", "SELECT * FROM ev WHERE created >= (current_date - 5)::timestamptz AND created < (current_date - 4)::timestamptz")

    print("\n3) LIKE: prefixo precisa de text_pattern_ops (em colações que não são C); contém ('%x%') precisa de trigramas")
    show("LIKE 'User5000%' (índice comum não ajuda)", "SELECT * FROM ev WHERE email LIKE 'User5000%'")
    conn.execute("CREATE INDEX ev_email_pattern ON ev (email text_pattern_ops)")
    conn.execute("ANALYZE ev")
    show("LIKE 'User5000%' com text_pattern_ops", "SELECT * FROM ev WHERE email LIKE 'User5000%'")
    show("LIKE '%ser5000%' (contém: sem índice)", "SELECT * FROM ev WHERE email LIKE '%ser5000%'")
    conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    conn.execute("CREATE INDEX ev_email_trgm ON ev USING gin (email gin_trgm_ops)")
    conn.execute("ANALYZE ev")
    show("LIKE '%ser5000%' com índice de trigramas (GIN)", "SELECT * FROM ev WHERE email LIKE '%ser5000%'")

    print("\n4) índice PARCIAL e de COBERTURA")
    conn.execute("ALTER TABLE ev ADD COLUMN done boolean NOT NULL DEFAULT true")
    conn.execute("UPDATE ev SET done = false WHERE id % 1000 = 0")
    conn.execute("CREATE INDEX ev_pending ON ev (id) WHERE NOT done")
    conn.execute("CREATE INDEX ev_all_done ON ev (id, done)")
    conn.execute("ANALYZE ev")
    size = {n: conn.execute("SELECT pg_size_pretty(pg_relation_size(%s))", (n,)).fetchone()[0] for n in ("ev_pending", "ev_all_done")}
    print(f"  índice parcial (só os 0,1% pendentes) = {size['ev_pending']} contra {size['ev_all_done']} do índice completo: menor, mais rápido de manter")
    show("WHERE NOT done (usa o parcial)", "SELECT id FROM ev WHERE NOT done")
    conn.execute("CREATE INDEX ev_cover ON ev (a) INCLUDE (b)")
    conn.execute("VACUUM ANALYZE ev")
    show("SELECT a, b ... WHERE a = 5 (índice de cobertura: só o índice)", "SELECT a, b FROM ev WHERE a = 5")

    print("\n5) o PREÇO dos índices: inserir 300.000 linhas")
    for label, indexes in (("sem índices (só a PK)", []), ("com 4 índices extras", ["(a)", "(b)", "(email)", "(payload)"])):
        table = "ins_" + str(len(indexes))
        conn.execute(f"CREATE TABLE {table} (id bigserial PRIMARY KEY, a int, b int, email text, payload text)")
        for definition in indexes:
            conn.execute(f"CREATE INDEX ON {table} {definition}")
        elapsed = timed(conn, f"INSERT INTO {table} (a, b, email, payload) SELECT g % 1000, g % 50, 'u' || g, md5(g::text) FROM generate_series(1, 300000) g")
        print(f"  {label:<26}{elapsed:>8.2f} s")
    unused = conn.execute("SELECT count(*) FROM pg_stat_user_indexes WHERE schemaname = 'lab60' AND idx_scan = 0").fetchone()[0]
    print(f"  índices que NUNCA foram usados neste laboratório: {unused} (em produção, pg_stat_user_indexes.idx_scan = 0 mostra os candidatos a remover)")
