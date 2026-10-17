"""Os erros de SQL mais caros, medidos (PostgreSQL)."""
import json

from lab import lab, plan, timed

with lab() as conn:
    # 1. NOT IN com NULL: resposta ERRADA em silêncio
    print("1) NOT IN com NULL na subconsulta")
    wrong = conn.execute("SELECT count(*) FROM generate_series(1, 5) g WHERE g NOT IN (SELECT x FROM (VALUES (1), (NULL)) v(x))").fetchone()[0]
    right = conn.execute("SELECT count(*) FROM generate_series(1, 5) g WHERE NOT EXISTS (SELECT 1 FROM (VALUES (1), (NULL)) v(x) WHERE v.x = g)").fetchone()[0]
    print(f"   NOT IN -> {wrong} linhas (!), NOT EXISTS -> {right} linhas. Um NULL na lista faz 'g NOT IN (...)' virar desconhecido para TODOS. Use NOT EXISTS.")

    # 2. linha a linha x conjunto
    conn.execute("CREATE TABLE up (id int PRIMARY KEY, v int DEFAULT 0)")
    conn.execute("INSERT INTO up SELECT g, 0 FROM generate_series(1, 20000) g")
    import time

    start = time.perf_counter()
    with conn.transaction():
        for i in range(1, 2001):
            conn.execute("UPDATE up SET v = v + 1 WHERE id = %s", (i,))
    row_by_row = (time.perf_counter() - start) * 10
    set_based = timed(conn, "UPDATE up SET v = v + 1")
    print(f"\n2) atualizar 20.000 linhas: laço de UPDATEs {row_by_row:.2f} s (estimado de 2.000) | UM UPDATE {set_based * 1e3:.0f} ms | {row_by_row / set_based:.0f}x")
    print("   pense em CONJUNTOS: o banco é feito para operar em muitas linhas por comando, não uma por ida e volta.")

    # 3. N+1 em SQL puro: um JOIN no lugar de 1 + N consultas
    conn.execute("CREATE TABLE author (id int PRIMARY KEY, name text)")
    conn.execute("CREATE TABLE book (id serial PRIMARY KEY, author_id int REFERENCES author(id), title text)")
    conn.execute("CREATE INDEX ON book (author_id)")
    conn.execute("INSERT INTO author SELECT g, 'a' || g FROM generate_series(1, 500) g")
    conn.execute("INSERT INTO book (author_id, title) SELECT g, 't' || g || '-' || j FROM generate_series(1, 500) g, generate_series(1, 5) j")
    start = time.perf_counter()
    authors = conn.execute("SELECT id FROM author").fetchall()
    total = sum(len(conn.execute("SELECT title FROM book WHERE author_id = %s", (a[0],)).fetchall()) for a in authors)
    n_plus_one = time.perf_counter() - start
    start = time.perf_counter()
    joined = conn.execute("SELECT a.id, b.title FROM author a JOIN book b ON b.author_id = a.id").fetchall()
    join = time.perf_counter() - start
    print(f"\n3) 500 autores x 5 livros: 501 consultas {n_plus_one * 1e3:.0f} ms | um JOIN {join * 1e3:.0f} ms | {n_plus_one / join:.0f}x ({total} = {len(joined)} linhas)")

    # 4. SELECT * e larguras
    conn.execute("CREATE TABLE wide (id int PRIMARY KEY, name text, doc text)")
    conn.execute("INSERT INTO wide SELECT g, 'n' || g, repeat('x', 2000) FROM generate_series(1, 50000) g")
    start = time.perf_counter()
    conn.execute("SELECT * FROM wide").fetchall()
    star = time.perf_counter() - start
    start = time.perf_counter()
    conn.execute("SELECT id, name FROM wide").fetchall()
    needed = time.perf_counter() - start
    print(f"\n4) 50.000 linhas com uma coluna de 2 KB: SELECT * {star * 1e3:.0f} ms | só id e name {needed * 1e3:.0f} ms | {star / needed:.0f}x (menos bytes na rede e na memória)")

    # 5. COUNT(*) exato x estimativa
    conn.execute("INSERT INTO up SELECT g, 0 FROM generate_series(20001, 2000000) g")
    conn.execute("ANALYZE up")
    start = time.perf_counter()
    exact = conn.execute("SELECT count(*) FROM up").fetchone()[0]
    count_time = time.perf_counter() - start
    estimate = conn.execute("SELECT reltuples::bigint FROM pg_class WHERE oid = 'up'::regclass").fetchone()[0]
    print(f"\n5) COUNT(*) em 2.000.000 de linhas: exato {exact:,} em {count_time * 1e3:.0f} ms | estimativa do catálogo {estimate:,} em <1 ms (para 'cerca de N linhas' na tela, a estimativa basta)")

    # 6. EAV x colunas x jsonb
    conn.execute("CREATE TABLE eav (entity int, attr text, value text)")
    conn.execute("CREATE INDEX ON eav (entity, attr)")
    conn.execute("INSERT INTO eav SELECT g, a, 'v' FROM generate_series(1, 20000) g, unnest(ARRAY['cor', 'peso', 'tamanho', 'marca']) a")
    conn.execute("CREATE TABLE wide_cols (entity int PRIMARY KEY, cor text, peso text, tamanho text, marca text)")
    conn.execute("INSERT INTO wide_cols SELECT g, 'v', 'v', 'v', 'v' FROM generate_series(1, 20000) g")
    start = time.perf_counter()
    conn.execute("SELECT e.entity, max(value) FILTER (WHERE attr = 'cor'), max(value) FILTER (WHERE attr = 'peso') FROM eav e GROUP BY entity").fetchall()
    eav = time.perf_counter() - start
    start = time.perf_counter()
    conn.execute("SELECT entity, cor, peso FROM wide_cols").fetchall()
    cols = time.perf_counter() - start
    print(f"\n6) EAV (uma linha por atributo) para ler 2 atributos de 20.000 entidades: {eav * 1e3:.0f} ms | colunas {cols * 1e3:.0f} ms | {eav / cols:.0f}x; sem tipos, sem restrições, consultas contorcidas")
    print("   atributos realmente variáveis: uma coluna JSONB com índice GIN (Capítulo 2), não EAV.")
