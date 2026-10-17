"""SQL Server com mssql-python (o driver oficial da Microsoft; não exige instalar o driver ODBC)."""
import datetime as dt
import decimal

import mssql_python

from envs import MSSQL_CS

print("mssql-python", getattr(mssql_python, "__version__", "?"))
admin = mssql_python.connect(MSSQL_CS.format(db="master"), autocommit=True)
admin.cursor().execute("IF DB_ID('livro') IS NULL CREATE DATABASE livro")
admin.close()

conn = mssql_python.connect(MSSQL_CS.format(db="livro"), autocommit=False)
cursor = conn.cursor()
cursor.execute("SELECT @@VERSION")
print(cursor.fetchone()[0].splitlines()[0])
cursor.execute("IF OBJECT_ID('demo') IS NOT NULL DROP TABLE demo")
cursor.execute("""CREATE TABLE demo (id INT IDENTITY(1, 1) PRIMARY KEY, name NVARCHAR(50) NOT NULL,
                  price DECIMAL(10, 2), at DATETIME2 DEFAULT SYSUTCDATETIME())""")

# placeholder ? ; OUTPUT INSERTED devolve as colunas geradas (como RETURNING)
cursor.execute("INSERT INTO demo (name, price) OUTPUT INSERTED.id, INSERTED.at VALUES (?, ?)", ("café \u2615", decimal.Decimal("9.90")))
row = cursor.fetchone()
print("OUTPUT INSERTED:", row[0], row[1], "| datetime2 volta SEM fuso:", row[1].tzinfo)
conn.commit()
cursor.execute("SELECT * FROM demo")
row = cursor.fetchone()
print("Row por nome e por posição:", row.name == row[1], "|", [type(value).__name__ for value in row])
print("NVARCHAR e Unicode:", row.name.encode("ascii", "backslashreplace").decode(), "| DECIMAL ->", repr(row.price))

# paginação: TOP e OFFSET/FETCH (este EXIGE ORDER BY)
for i in range(30):
    cursor.execute("INSERT INTO demo (name) VALUES (?)", (f"n{i}",))
conn.commit()
cursor.execute("SELECT name FROM demo ORDER BY id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY", (10, 3))
print("OFFSET/FETCH:", cursor.fetchall())
cursor.execute("SELECT TOP (?) name FROM demo ORDER BY id", (2,))
print("TOP:", [r[0].encode("ascii", "backslashreplace").decode() for r in cursor.fetchall()])
try:
    cursor.execute("SELECT name FROM demo OFFSET 0 ROWS FETCH NEXT 3 ROWS ONLY")
except Exception as error:
    print("OFFSET sem ORDER BY:", type(error).__name__)
    conn.rollback()

# MERGE (o upsert); T-SQL exige o ponto e vírgula no fim
cursor.execute("IF OBJECT_ID('cnt') IS NOT NULL DROP TABLE cnt")
cursor.execute("CREATE TABLE cnt (w VARCHAR(10) PRIMARY KEY, n INT)")
for word in "a b a c a".split():
    cursor.execute("""MERGE cnt AS t USING (SELECT ? AS w) AS s ON t.w = s.w
                      WHEN MATCHED THEN UPDATE SET n = n + 1
                      WHEN NOT MATCHED THEN INSERT (w, n) VALUES (s.w, 1);""", (word,))
conn.commit()
cursor.execute("SELECT w, n FROM cnt ORDER BY w")
print("MERGE:", [tuple(r) for r in cursor.fetchall()])

# no T-SQL o DDL É transacional (diferente de MySQL e Oracle)
cursor.execute("INSERT INTO cnt VALUES ('zz', 1)")
cursor.execute("CREATE TABLE ddl_marker (x INT)")
conn.rollback()
cursor.execute("SELECT COUNT(*) FROM cnt WHERE w = 'zz'")
print("DDL e rollback: linhas 'zz' =", cursor.fetchone()[0], "(o rollback desfez também o CREATE TABLE)")

# erros viram classes do DB-API
try:
    cursor.execute("INSERT INTO cnt VALUES ('a', 1)")
except mssql_python.IntegrityError as error:
    print("IntegrityError:", str(error)[:70])
    conn.rollback()
for table in ("demo", "cnt"):
    cursor.execute(f"DROP TABLE {table}")
conn.commit()
conn.close()
