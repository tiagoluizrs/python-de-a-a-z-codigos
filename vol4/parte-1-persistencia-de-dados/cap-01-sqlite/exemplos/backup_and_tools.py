"""Backup, serialização, dump e o CLI embutido."""
import os
import sqlite3
import tempfile

src = sqlite3.connect(":memory:")
src.execute("CREATE TABLE t (x INTEGER)")
src.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(1000)])
src.commit()

# backup online: copia um banco VIVO de forma consistente
path = os.path.join(tempfile.mkdtemp(), "copia.db")
dest = sqlite3.connect(path)
src.backup(dest)
print("backup para arquivo:", dest.execute("SELECT COUNT(*) FROM t").fetchone()[0], "linhas;", os.path.getsize(path), "bytes")
dest.close()

# serialize/deserialize: o banco inteiro como bytes
blob = src.serialize()
print("serialize():", type(blob).__name__, len(blob), "bytes")
clone = sqlite3.connect(":memory:")
clone.deserialize(blob)
print("deserialize(): clone tem", clone.execute("SELECT COUNT(*) FROM t").fetchone()[0], "linhas")

# dump em SQL (texto)
small = sqlite3.connect(":memory:")
small.execute("CREATE TABLE p (id INTEGER PRIMARY KEY, name TEXT)")
small.executemany("INSERT INTO p (name) VALUES (?)", [("ana",), ("bia",)])
small.commit()
print("iterdump():")
for line in small.iterdump():
    print("  ", line)

# URI: modo somente leitura e memória compartilhada entre conexões
os.environ.setdefault("X", "1")
ro = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
try:
    ro.execute("INSERT INTO t VALUES (1)")
except sqlite3.OperationalError as error:
    print("modo ro:", error)
ro.close()
a = sqlite3.connect("file:memdb1?mode=memory&cache=shared", uri=True)
a.execute("CREATE TABLE s (v)")
a.execute("INSERT INTO s VALUES (42)")
a.commit()
b = sqlite3.connect("file:memdb1?mode=memory&cache=shared", uri=True)
print("memória compartilhada entre duas conexões:", b.execute("SELECT v FROM s").fetchone())
print("CLI embutido:  python -m sqlite3 loja.db   (um shell SQL interativo, sem instalar nada)")
