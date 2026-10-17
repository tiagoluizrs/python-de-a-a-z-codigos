"""Gabarito do exercício 3."""
import sqlite3

CHUNK = 500


class QueryCounter:
    def __init__(self, conn):
        self.conn = conn
        self._statements = []

    def __enter__(self):
        self._statements = []
        self.conn.set_trace_callback(self._statements.append)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.set_trace_callback(None)
        return False

    @property
    def statements(self):
        return [s for s in self._statements if s.lstrip().upper().startswith("SELECT")]

    @property
    def count(self):
        return len(self.statements)


def titles_naive(conn):
    result = {}
    for author_id, name in conn.execute("SELECT id, name FROM authors ORDER BY name").fetchall():
        rows = conn.execute("SELECT title FROM books WHERE author_id = ? ORDER BY title", (author_id,)).fetchall()
        result[name] = [title for (title,) in rows]
    return result


def titles_in(conn):
    authors = conn.execute("SELECT id, name FROM authors ORDER BY name").fetchall()
    titles = {author_id: [] for author_id, _ in authors}
    ids = [author_id for author_id, _ in authors]
    for start in range(0, len(ids), CHUNK):
        chunk = ids[start:start + CHUNK]
        marks = ", ".join("?" * len(chunk))
        for author_id, title in conn.execute(f"SELECT author_id, title FROM books WHERE author_id IN ({marks}) ORDER BY title", chunk):
            titles[author_id].append(title)
    return {name: titles[author_id] for author_id, name in authors}


def titles_join(conn):
    result = {}
    rows = conn.execute("SELECT a.name, b.title FROM authors a LEFT JOIN books b ON b.author_id = a.id ORDER BY a.name, b.title")
    for name, title in rows:
        titles = result.setdefault(name, [])
        if title is not None:
            titles.append(title)
    return result
