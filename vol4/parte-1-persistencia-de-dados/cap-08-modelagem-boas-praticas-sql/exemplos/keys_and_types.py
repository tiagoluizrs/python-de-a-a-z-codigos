"""Chaves e tipos: bigint x UUID, dinheiro, data e hora, restrições (PostgreSQL 18)."""
import decimal
import uuid

from lab import lab, timed

with lab() as conn:
    version = conn.execute("SHOW server_version").fetchone()[0]
    print("PostgreSQL", version)
    N = 300_000
    print(f"1) chave primária: inserir {N:,} linhas")
    print(f"   {'tipo da chave':<30}{'tempo':>9}{'índice da PK':>16}")
    for label, table, ddl in (("bigint (identidade)", "k_bigint", "id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY"),
                              ("uuid v4 (aleatório)", "k_uuid4", "id uuid PRIMARY KEY DEFAULT gen_random_uuid()"),
                              ("uuid v7 (ordenado por tempo)", "k_uuid7", "id uuid PRIMARY KEY DEFAULT uuidv7()")):
        conn.execute(f"CREATE TABLE {table} ({ddl}, payload text)")
        elapsed = timed(conn, f"INSERT INTO {table} (payload) SELECT md5(g::text) FROM generate_series(1, {N}) g")
        size = conn.execute(f"SELECT pg_size_pretty(pg_relation_size('{table}_pkey'))").fetchone()[0]
        print(f"   {label:<30}{elapsed:>8.2f}s{size:>16}")
    print("   UUID v4 é aleatório: cada inserção cai em um ponto qualquer do índice (páginas divididas, cache frio).")
    print("   UUID v7 começa com o tempo: inserções quase sequenciais, como o bigint, e ainda assim globalmente únicas.")
    print("   Chave NATURAL (CPF, e-mail, SKU) muda e se repete entre sistemas; prefira uma chave SUBSTITUTA estável e deixe a natural como UNIQUE.")

    print("\n2) dinheiro: float x numeric")
    print("   float8 : soma de 0.1 dez vezes =", conn.execute("SELECT sum(0.1::float8) FROM generate_series(1, 10)").fetchone()[0], "| 0.1*3 = 0.3?", conn.execute("SELECT 0.1::float8 * 3 = 0.3::float8").fetchone()[0])
    print("   numeric: soma de 0.1 dez vezes =", conn.execute("SELECT sum(0.1::numeric) FROM generate_series(1, 10)").fetchone()[0], "| 0.1*3 = 0.3?", conn.execute("SELECT 0.1::numeric * 3 = 0.3::numeric").fetchone()[0])
    print("   regra: dinheiro é numeric(p, s) (ou inteiro em centavos), NUNCA float.")

    print("\n3) data e hora: timestamp x timestamptz")
    conn.execute("SET TIME ZONE 'UTC'")
    conn.execute("CREATE TABLE t (naive timestamp, aware timestamptz)")
    conn.execute("INSERT INTO t VALUES ('2026-10-13 12:00-03', '2026-10-13 12:00-03')")
    conn.execute("SET TIME ZONE 'America/Recife'")
    row = conn.execute("SELECT naive, aware FROM t").fetchone()
    print(f"   gravado '12:00-03'; lendo com a sessão em Recife -> timestamp: {row[0]} (descartou o -03 em silêncio: ninguém sabe mais em que fuso era) | timestamptz: {row[1]} (o MESMO instante, na zona da sessão)")
    print("   regra: instantes são timestamptz (guardados em UTC); timestamp sem fuso só para 'datas de calendário' sem instante.")

    print("\n4) texto: varchar(n) x text")
    conn.execute("CREATE TABLE s (a varchar(10), b text)")
    print("   no PostgreSQL text e varchar(n) têm o MESMO desempenho; varchar(n) só vale se o limite é regra de negócio (use CHECK ou o tamanho do padrão).")

    print("\n5) restrições no banco: o último muro")
    conn.execute("""CREATE TABLE product (
        id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, sku text NOT NULL UNIQUE,
        price numeric(10, 2) NOT NULL CHECK (price >= 0), status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')))""")
    for sql in ("INSERT INTO product (sku, price) VALUES ('A', -1)", "INSERT INTO product (sku, price, status) VALUES ('B', 1, 'apagado')", "INSERT INTO product (sku, price) VALUES (NULL, 1)"):
        try:
            conn.execute(sql)
        except Exception as error:
            print(f"   recusado: {type(error).__name__}")
    print("   (um bug na aplicação, um script manual ou outro sistema também passam por estas regras)")
