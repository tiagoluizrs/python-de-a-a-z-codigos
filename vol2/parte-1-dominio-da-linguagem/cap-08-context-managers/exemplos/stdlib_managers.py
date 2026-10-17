"""Gerenciadores que a biblioteca padrão já traz."""
import decimal
import sqlite3
import tempfile
import threading
import warnings
import zipfile
from pathlib import Path

# Lock: garante o release
lock = threading.Lock()
with lock:
    print("lock tomado:", lock.locked())
print("lock liberado:", not lock.locked())

# decimal.localcontext: precisão só dentro do bloco
with decimal.localcontext() as ctx:
    ctx.prec = 5
    print(decimal.Decimal(1) / decimal.Decimal(7))
print(decimal.Decimal(1) / decimal.Decimal(7))

# warnings.catch_warnings: captura avisos sem poluir o resto do programa
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    warnings.warn("cuidado", UserWarning)
print([str(w.message) for w in caught])

# TemporaryDirectory: apaga tudo no fim
with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "a.txt").write_text("x")
    print("existe dentro:", Path(tmp).exists())
print("existe depois:", Path(tmp).exists())

# zipfile
with tempfile.TemporaryDirectory() as tmp:
    archive = Path(tmp) / "a.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("hello.txt", "olá")
    with zipfile.ZipFile(archive) as zf:
        print(zf.namelist())

# PEGADINHA: `with sqlite3.connect(...)` NÃO fecha a conexão:
# ele só faz commit (ou rollback se houver exceção)
conn = sqlite3.connect(":memory:")
with conn:
    conn.execute("create table t (x)")
    conn.execute("insert into t values (1)")
try:
    conn.execute("select * from t")
    print("a conexão continua aberta depois do with")
finally:
    conn.close()
