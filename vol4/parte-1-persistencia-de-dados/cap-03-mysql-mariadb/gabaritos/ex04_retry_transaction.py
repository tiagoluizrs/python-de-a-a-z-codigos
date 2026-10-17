"""Gabarito do exercício 4."""
import time

import pymysql

RETRYABLE = (1213, 1205)


def run_with_retry(func, attempts=3, delay=0.05, sleep=time.sleep):
    if attempts < 1:
        raise ValueError("attempts >= 1")
    for failures in range(attempts):
        try:
            return func()
        except pymysql.err.OperationalError as error:
            if error.args[0] not in RETRYABLE or failures == attempts - 1:
                raise
            sleep(delay * 2**failures)


def transfer(conn, source_id, target_id, amount):
    if source_id == target_id or amount <= 0:
        raise ValueError("contas iguais ou valor inválido")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, balance FROM account WHERE id IN (%s, %s) ORDER BY id FOR UPDATE", (source_id, target_id))
            balances = {row["id"]: row["balance"] for row in cursor.fetchall()}
            if len(balances) != 2:
                raise ValueError("conta inexistente")
            if balances[source_id] < amount:
                raise ValueError("saldo insuficiente")
            cursor.execute("UPDATE account SET balance = balance - %s WHERE id = %s", (amount, source_id))
            cursor.execute("UPDATE account SET balance = balance + %s WHERE id = %s", (amount, target_id))
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
