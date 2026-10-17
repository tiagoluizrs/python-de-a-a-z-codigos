"""Gabarito do exercício 2."""
import psycopg


class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_schema(self):
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS app_user (id bigserial PRIMARY KEY, email text NOT NULL, "
            "name text NOT NULL, created_at timestamptz NOT NULL DEFAULT now())")
        self.conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS app_user_email_ci ON app_user (lower(email))")
        self.conn.commit()

    def add(self, email, name):
        try:
            row = self.conn.execute("INSERT INTO app_user (email, name) VALUES (%s, %s) RETURNING *", (email, name)).fetchone()
        except psycopg.errors.UniqueViolation as error:
            self.conn.rollback()
            raise ValueError(f"e-mail já cadastrado: {email!r}") from error
        self.conn.commit()
        return row

    def get_by_email(self, email):
        row = self.conn.execute("SELECT * FROM app_user WHERE lower(email) = lower(%s)", (email,)).fetchone()
        self.conn.rollback()
        return row

    def rename(self, user_id, name):
        cursor = self.conn.execute("UPDATE app_user SET name = %s WHERE id = %s", (name, user_id))
        self.conn.commit()
        return cursor.rowcount == 1

    def page(self, after_id=None, limit=3):
        rows = self.conn.execute(
            "SELECT * FROM app_user WHERE id > %s ORDER BY id LIMIT %s", (after_id if after_id is not None else 0, limit + 1)).fetchall()
        self.conn.rollback()
        if len(rows) > limit:
            rows = rows[:limit]
            return rows, rows[-1]["id"]
        return rows, None
