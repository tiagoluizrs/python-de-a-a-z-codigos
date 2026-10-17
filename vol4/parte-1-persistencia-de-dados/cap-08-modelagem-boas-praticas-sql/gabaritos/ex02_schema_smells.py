"""Gabarito do exercício 2."""
_MONEY = ("price", "preco", "amount", "valor", "total", "balance", "saldo")


def schema_smells(conn):
    found = set()
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        columns = conn.execute(f'PRAGMA table_info("{table}")').fetchall()          # cid, name, type, notnull, dflt, pk
        if not any(c[5] for c in columns):
            found.add(("sem_chave_primaria", table, None))
        first_pk = next((c[1] for c in sorted(columns, key=lambda c: c[5]) if c[5] == 1), None)
        indexed_first = set()
        for index in conn.execute(f'PRAGMA index_list("{table}")').fetchall():
            info = conn.execute(f'PRAGMA index_info("{index[1]}")').fetchall()
            if info:
                indexed_first.add(info[0][2])
            if index[2]:                                                              # índice único
                for _seq, _cid, name in info:
                    column = next(c for c in columns if c[1] == name)
                    if not column[3] and not column[5]:
                        found.add(("coluna_nula_na_pk_unica", table, name))
        if first_pk:
            indexed_first.add(first_pk)
        for fk in conn.execute(f'PRAGMA foreign_key_list("{table}")').fetchall():
            if fk[3] not in indexed_first:
                found.add(("fk_sem_indice", table, fk[3]))
        for column in columns:
            kind = (column[2] or "").upper()
            if any(k in kind for k in ("REAL", "FLOAT", "DOUBLE")) and any(m in column[1].lower() for m in _MONEY):
                found.add(("dinheiro_em_float", table, column[1]))
    return sorted(found, key=lambda t: (t[0], t[1], t[2] or ""))
