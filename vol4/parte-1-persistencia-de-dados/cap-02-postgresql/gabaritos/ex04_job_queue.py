"""Gabarito do exercício 4."""
import time


def create_schema(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS job (id bigserial PRIMARY KEY, payload text NOT NULL, "
        "state text NOT NULL DEFAULT 'new' CHECK (state IN ('new', 'running', 'done')), owner text)")
    conn.commit()


def enqueue(conn, payloads):
    ids = []
    with conn.transaction():
        for payload in payloads:
            ids.append(conn.execute("INSERT INTO job (payload) VALUES (%s) RETURNING id", (payload,)).fetchone()["id"])
    return ids


def claim(conn, worker, limit=5, hold=0.0):
    with conn.transaction():
        rows = conn.execute(
            """UPDATE job SET state = 'running', owner = %s
               WHERE id IN (SELECT id FROM job WHERE state = 'new' ORDER BY id LIMIT %s FOR UPDATE SKIP LOCKED)
               RETURNING id""", (worker, limit)).fetchall()
        if hold:
            time.sleep(hold)
    return sorted(row["id"] for row in rows)


def finish(conn, job_id, worker):
    with conn.transaction():
        cursor = conn.execute("UPDATE job SET state = 'done' WHERE id = %s AND state = 'running' AND owner = %s", (job_id, worker))
    return cursor.rowcount == 1
