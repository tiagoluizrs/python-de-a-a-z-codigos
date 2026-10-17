"""Restrições além do básico: ações de FK, índice único parcial, exclusão (PostgreSQL)."""
import psycopg

from lab import lab

with lab() as conn:
    # 1. o que acontece quando o pai é apagado: RESTRICT, CASCADE ou SET NULL
    conn.execute("CREATE TABLE author (id int PRIMARY KEY, name text)")
    conn.execute("CREATE TABLE book_restrict (id serial PRIMARY KEY, author_id int REFERENCES author(id) ON DELETE RESTRICT)")
    conn.execute("CREATE TABLE book_cascade (id serial PRIMARY KEY, author_id int REFERENCES author(id) ON DELETE CASCADE)")
    conn.execute("CREATE TABLE book_setnull (id serial PRIMARY KEY, author_id int REFERENCES author(id) ON DELETE SET NULL)")
    conn.execute("INSERT INTO author VALUES (1, 'Machado'), (2, 'Clarice'), (3, 'Lispector')")
    for table, author in (("book_restrict", 1), ("book_cascade", 2), ("book_setnull", 3)):
        conn.execute(f"INSERT INTO {table} (author_id) VALUES (%s), (%s)", (author, author))
    try:
        conn.execute("DELETE FROM author WHERE id = 1")
    except psycopg.errors.RestrictViolation:
        print("RESTRICT: apagar o autor com livros é RECUSADO (o padrão seguro)")
    conn.execute("DELETE FROM author WHERE id = 2")
    print("CASCADE : apagou o autor 2 e os livros dele sumiram junto ->", conn.execute("SELECT count(*) FROM book_cascade").fetchone()[0], "livros (cuidado: apaga dados em cadeia)")
    conn.execute("DELETE FROM author WHERE id = 3")
    print("SET NULL: apagou o autor 3; os livros ficaram órfãos de propósito ->", conn.execute("SELECT count(*) FROM book_setnull WHERE author_id IS NULL").fetchone()[0], "com author_id NULL")

    # 2. 'exclusão lógica' (soft delete) + índice ÚNICO PARCIAL: o e-mail é único só entre os ativos
    conn.execute("CREATE TABLE app_user (id serial PRIMARY KEY, email text NOT NULL, deleted_at timestamptz)")
    conn.execute("CREATE UNIQUE INDEX uq_user_email_active ON app_user (lower(email)) WHERE deleted_at IS NULL")
    conn.execute("INSERT INTO app_user (email) VALUES ('ana@x.com')")
    try:
        conn.execute("INSERT INTO app_user (email) VALUES ('ANA@x.com')")
    except psycopg.errors.UniqueViolation:
        print("\nUNIQUE parcial: um 2º cadastro ativo do mesmo e-mail é recusado (ignorando maiúsculas)")
    conn.execute("UPDATE app_user SET deleted_at = now() WHERE email = 'ana@x.com'")
    conn.execute("INSERT INTO app_user (email) VALUES ('ana@x.com')")
    print("depois de 'apagar' (deleted_at), o mesmo e-mail pode se cadastrar de novo:", conn.execute("SELECT count(*) FROM app_user").fetchone()[0], "linhas (1 apagada, 1 ativa)")
    print("custo da exclusão lógica: TODA consulta precisa de 'deleted_at IS NULL' (esqueça em um lugar e o dado 'apagado' reaparece); uma VIEW ajuda.")

    # 3. restrição de EXCLUSÃO: reservas que não se sobrepõem (impossível com UNIQUE)
    conn.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    conn.execute("""CREATE TABLE booking (room int, during tstzrange, EXCLUDE USING gist (room WITH =, during WITH &&))""")
    conn.execute("INSERT INTO booking VALUES (1, '[2026-10-13 09:00, 2026-10-13 11:00)')")
    conn.execute("INSERT INTO booking VALUES (2, '[2026-10-13 09:00, 2026-10-13 11:00)')")                    # outra sala: ok
    conn.execute("INSERT INTO booking VALUES (1, '[2026-10-13 11:00, 2026-10-13 12:00)')")                    # encosta, não sobrepõe: ok
    try:
        conn.execute("INSERT INTO booking VALUES (1, '[2026-10-13 10:00, 2026-10-13 10:30)')")
    except psycopg.errors.ExclusionViolation:
        print("\nEXCLUDE: a reserva da sala 1 às 10:00 SOBREPÕE a das 09:00-11:00 e foi recusada pelo banco (sem corrida, sem trava na aplicação)")
