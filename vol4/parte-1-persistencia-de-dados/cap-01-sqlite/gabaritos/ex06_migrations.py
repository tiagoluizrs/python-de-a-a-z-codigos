"""Gabarito do exercício 6."""


def apply_migrations(conn, migrations):
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version > len(migrations):
        raise RuntimeError(f"banco na versão {version}, mais novo que as {len(migrations)} migrações conhecidas")
    for index in range(version, len(migrations)):
        conn.commit()
        try:
            # executescript roda vários comandos; o BEGIN/COMMIT explícito torna a migração atômica
            conn.executescript("BEGIN;" + chr(10) + migrations[index] + chr(10) + f"PRAGMA user_version = {index + 1};" + chr(10) + "COMMIT;")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
    return conn.execute("PRAGMA user_version").fetchone()[0]
