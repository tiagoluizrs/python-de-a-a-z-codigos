"""Um linter de esquema: o que revisar em um banco existente (PostgreSQL)."""
from lab import lab

SMELLS = """
-- tabela sem chave primária
SELECT 'sem_chave_primaria', c.relname, NULL FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = current_schema() AND c.relkind = 'r' AND NOT EXISTS (SELECT 1 FROM pg_constraint k WHERE k.conrelid = c.oid AND k.contype = 'p')
UNION ALL
-- coluna de chave estrangeira sem índice (junções e DELETE no pai ficam lentos)
SELECT 'fk_sem_indice', c.relname, a.attname FROM pg_constraint k JOIN pg_class c ON c.oid = k.conrelid
JOIN pg_namespace n ON n.oid = c.relnamespace JOIN pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = k.conkey[1]
WHERE k.contype = 'f' AND n.nspname = current_schema() AND NOT EXISTS (
    SELECT 1 FROM pg_index i WHERE i.indrelid = k.conrelid AND i.indkey[0] = k.conkey[1])
UNION ALL
-- dinheiro em ponto flutuante
SELECT 'dinheiro_em_float', table_name, column_name FROM information_schema.columns
WHERE table_schema = current_schema() AND data_type IN ('real', 'double precision') AND column_name ~* '(price|preco|amount|valor|total|balance|saldo)'
UNION ALL
-- instante sem fuso
SELECT 'timestamp_sem_fuso', table_name, column_name FROM information_schema.columns
WHERE table_schema = current_schema() AND data_type = 'timestamp without time zone'
UNION ALL
-- índices duplicados (mesmas colunas, mesma tabela)
SELECT 'indice_duplicado', c.relname, string_agg(ic.relname, ', ') FROM pg_index i JOIN pg_class c ON c.oid = i.indrelid JOIN pg_class ic ON ic.oid = i.indexrelid
JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = current_schema() GROUP BY c.relname, i.indkey::text, i.indpred::text HAVING count(*) > 1
UNION ALL
-- coluna que parece guardar lista (CSV em texto)
SELECT 'lista_em_coluna', table_name, column_name FROM information_schema.columns
WHERE table_schema = current_schema() AND column_name ~* '(ids|tags|list|lista)$' AND data_type IN ('text', 'character varying')
ORDER BY 1, 2
"""

with lab() as conn:
    # um esquema CHEIO de problemas, de propósito
    conn.execute("CREATE TABLE customer (id serial PRIMARY KEY, name text, tags text, created timestamp)")
    conn.execute("CREATE TABLE orders (id serial PRIMARY KEY, customer_id int REFERENCES customer(id), total double precision, price real)")
    conn.execute("CREATE TABLE log_entry (message text, at timestamp)")
    conn.execute("CREATE INDEX ix_customer_name_1 ON customer (name)")
    conn.execute("CREATE INDEX ix_customer_name_2 ON customer (name)")
    print("esquema ruim, de propósito:")
    for code, table, column in conn.execute(SMELLS):
        print(f"   [{code}] {table}" + (f".{column}" if column else ""))

    # a versão corrigida
    conn.execute("DROP SCHEMA lab60 CASCADE")
    conn.execute("CREATE SCHEMA lab60")
    conn.execute("SET search_path = lab60")
    conn.execute("CREATE TABLE customer (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, name text NOT NULL, created timestamptz NOT NULL DEFAULT now())")
    conn.execute("CREATE TABLE tag (customer_id bigint REFERENCES customer(id) ON DELETE CASCADE, tag text NOT NULL, PRIMARY KEY (customer_id, tag))")
    conn.execute("CREATE TABLE orders (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, customer_id bigint NOT NULL REFERENCES customer(id), total numeric(12, 2) NOT NULL CHECK (total >= 0))")
    conn.execute("CREATE INDEX ix_orders_customer ON orders (customer_id)")
    print("\nesquema corrigido:", [tuple(r) for r in conn.execute(SMELLS)] or "nenhum problema encontrado")
