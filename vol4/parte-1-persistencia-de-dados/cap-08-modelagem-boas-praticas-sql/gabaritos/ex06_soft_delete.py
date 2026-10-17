"""Gabarito do exercício 6."""
import sqlite3


class SoftDeleteUsers:
    def __init__(self, conn):
        self.conn = conn

    def create_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS app_user (id INTEGER PRIMARY KEY, email TEXT NOT NULL, name TEXT NOT NULL, deleted_at TEXT);
            CREATE UNIQUE INDEX IF NOT EXISTS uq_user_email_active ON app_user (lower(email)) WHERE deleted_at IS NULL;
            CREATE VIEW IF NOT EXISTS active_user AS SELECT id, email, name FROM app_user WHERE deleted_at IS NULL;""")
        self.conn.commit()

    def add(self, email, name):
        try:
            cursor = self.conn.execute("INSERT INTO app_user (email, name) VALUES (?, ?)", (email, name))
        except sqlite3.IntegrityError as error:
            self.conn.rollback()
            raise ValueError(f"e-mail já ativo: {email!r}") from error
        self.conn.commit()
        return cursor.lastrowid

    def delete(self, user_id, now):
        cursor = self.conn.execute("UPDATE app_user SET deleted_at = ? WHERE id = ? AND deleted_at IS NULL", (now, user_id))
        self.conn.commit()
        return cursor.rowcount == 1

    def restore(self, user_id):
        try:
            cursor = self.conn.execute("UPDATE app_user SET deleted_at = NULL WHERE id = ? AND deleted_at IS NOT NULL", (user_id,))
        except sqlite3.IntegrityError as error:
            self.conn.rollback()
            raise ValueError("já existe outro usuário ativo com este e-mail") from error
        self.conn.commit()
        return cursor.rowcount == 1

    def purge(self, before_iso):
        cursor = self.conn.execute("DELETE FROM app_user WHERE deleted_at IS NOT NULL AND deleted_at < ?", (before_iso,))
        self.conn.commit()
        return cursor.rowcount

    def active_emails(self):
        return sorted(r[0] for r in self.conn.execute("SELECT email FROM active_user"))
