"""Gabarito do exercício 5."""


def transfer(conn, source_id, target_id, amount):
    if source_id == target_id or amount <= 0:
        raise ValueError("contas iguais ou valor inválido")
    with conn.transaction():
        rows = conn.execute("SELECT id, balance FROM account WHERE id IN (%s, %s) ORDER BY id FOR UPDATE", (source_id, target_id)).fetchall()
        balances = {row["id"]: row["balance"] for row in rows}
        if len(balances) != 2:
            raise ValueError("conta inexistente")
        if balances[source_id] < amount:
            raise ValueError("saldo insuficiente")
        conn.execute("UPDATE account SET balance = balance - %s WHERE id = %s", (amount, source_id))
        conn.execute("UPDATE account SET balance = balance + %s WHERE id = %s", (amount, target_id))
