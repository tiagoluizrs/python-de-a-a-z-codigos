"""Padrões de projeto: histórico por gatilho, e partição por faixa (PostgreSQL)."""
import time

from lab import lab

with lab() as conn:
    # 1. trilha de auditoria: um gatilho grava QUEM mudou O QUÊ e QUANDO, sem depender da aplicação
    conn.execute("CREATE TABLE account (id int PRIMARY KEY, owner text, balance numeric NOT NULL)")
    conn.execute("CREATE TABLE account_audit (at timestamptz DEFAULT now(), op text, old_row jsonb, new_row jsonb)")
    conn.execute("""CREATE FUNCTION audit() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO account_audit (op, old_row, new_row)
            VALUES (TG_OP, CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END, CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END);
            RETURN NULL;
        END $$""")
    conn.execute("CREATE TRIGGER account_audit_trg AFTER INSERT OR UPDATE OR DELETE ON account FOR EACH ROW EXECUTE FUNCTION audit()")
    conn.execute("INSERT INTO account VALUES (1, 'ana', 100)")
    conn.execute("UPDATE account SET balance = 70 WHERE id = 1")
    conn.execute("DELETE FROM account WHERE id = 1")
    print("1) auditoria por gatilho:")
    for op, old, new in conn.execute("SELECT op, old_row ->> 'balance', new_row ->> 'balance' FROM account_audit ORDER BY at, op DESC"):
        print(f"   {op:<7} saldo antigo={old} novo={new}")
    print("   o histórico vive no banco: vale também para scripts manuais e outros sistemas (custo: cada escrita faz uma escrita a mais).")

    # 2. dados temporais: validade de cada versão da linha
    conn.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    conn.execute("CREATE TABLE price_history (product int, price numeric, valid tstzrange, EXCLUDE USING gist (product WITH =, valid WITH &&))")
    conn.execute("INSERT INTO price_history VALUES (1, 10, '[2026-01-01, 2026-06-01)'), (1, 12, '[2026-06-01, infinity)')")
    price = conn.execute("SELECT price FROM price_history WHERE product = 1 AND valid @> '2026-03-15'::timestamptz").fetchone()[0]
    print(f"\n2) preço histórico: em 15/03/2026 o produto 1 custava {price} (cada versão guarda o seu intervalo de validade, sem sobreposição)")

    # 3. particionamento por faixa: a consulta lê só a partição certa
    conn.execute("CREATE TABLE metric (ts timestamptz NOT NULL, v int) PARTITION BY RANGE (ts)")
    for month in range(1, 13):
        start = f"2026-{month:02d}-01"
        end = f"2026-{month + 1:02d}-01" if month < 12 else "2027-01-01"
        conn.execute(f"CREATE TABLE metric_{month:02d} PARTITION OF metric FOR VALUES FROM ('{start}') TO ('{end}')")
    conn.execute("INSERT INTO metric SELECT '2026-01-01'::timestamptz + (g || ' minutes')::interval, g FROM generate_series(1, 500000) g")
    conn.execute("ANALYZE metric")
    query = "SELECT count(*) FROM metric WHERE ts >= '2026-03-01' AND ts < '2026-04-01'"
    plan = [row[0] for row in conn.execute("EXPLAIN " + query)]
    scanned = [line.split(" on ")[1].split(" ")[0] for line in plan if "Scan on" in line]
    print(f"\n3) 500.000 linhas em 12 partições mensais: a consulta de março lê {len(scanned)} partição: {scanned} (poda de partições)")
    start_time = time.perf_counter()
    conn.execute(query).fetchone()
    pruned = time.perf_counter() - start_time
    conn.execute("CREATE TABLE metric_flat (ts timestamptz NOT NULL, v int)")
    conn.execute("INSERT INTO metric_flat SELECT ts, v FROM metric")
    conn.execute("ANALYZE metric_flat")
    start_time = time.perf_counter()
    conn.execute(query.replace("metric", "metric_flat")).fetchone()
    flat = time.perf_counter() - start_time
    print(f"   particionada {pruned * 1e3:.1f} ms | tabela única {flat * 1e3:.1f} ms")
    start_time = time.perf_counter()
    conn.execute("DROP TABLE metric_01")
    print(f"   apagar um mês inteiro: DROP TABLE da partição em {(time.perf_counter() - start_time) * 1e3:.1f} ms (um DELETE de milhões de linhas levaria segundos e deixaria 'lixo')")
    print("   particione tabelas MUITO grandes de eventos/métricas com retenção por tempo; para tabelas médias, índices bastam.")
