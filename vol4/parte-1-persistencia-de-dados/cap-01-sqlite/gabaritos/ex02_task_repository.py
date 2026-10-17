"""Gabarito do exercício 2."""
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool


class TaskRepository:
    def __init__(self, conn):
        self.conn = conn

    @staticmethod
    def _task(row):
        return Task(row["id"], row["title"], bool(row["done"]))

    def create_schema(self):
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS task (id INTEGER PRIMARY KEY, title TEXT NOT NULL UNIQUE "
            "CHECK (length(trim(title)) > 0), done INTEGER NOT NULL DEFAULT 0)")
        self.conn.commit()

    def add(self, title):
        try:
            row = self.conn.execute("INSERT INTO task (title) VALUES (?) RETURNING *", (title,)).fetchone()
        except sqlite3.IntegrityError as error:
            self.conn.rollback()
            raise ValueError(f"título inválido ou duplicado: {title!r}") from error
        self.conn.commit()
        return self._task(row)

    def get(self, task_id):
        row = self.conn.execute("SELECT * FROM task WHERE id = ?", (task_id,)).fetchone()
        return self._task(row) if row else None

    def list(self, done=None):
        sql, params = "SELECT * FROM task", ()
        if done is not None:
            sql, params = sql + " WHERE done = ?", (int(done),)
        return [self._task(r) for r in self.conn.execute(sql + " ORDER BY id", params)]

    def complete(self, task_id):
        cursor = self.conn.execute("UPDATE task SET done = 1 WHERE id = ? AND done = 0", (task_id,))
        self.conn.commit()
        return cursor.rowcount == 1

    def delete(self, task_id):
        cursor = self.conn.execute("DELETE FROM task WHERE id = ?", (task_id,))
        self.conn.commit()
        return cursor.rowcount == 1

    def stats(self):
        row = self.conn.execute("SELECT COUNT(*) AS total, COALESCE(SUM(done), 0) AS done FROM task").fetchone()
        return {"total": row["total"], "done": row["done"], "pending": row["total"] - row["done"]}
