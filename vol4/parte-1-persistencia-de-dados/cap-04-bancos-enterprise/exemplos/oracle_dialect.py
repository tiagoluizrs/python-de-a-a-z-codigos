"""Dialeto Oracle: paginação, MERGE, PL/SQL e async."""
import asyncio

import oracledb

from envs import ORACLE

conn = oracledb.connect(**ORACLE)
cursor = conn.cursor()
for table in ("item", "cnt"):
    try:
        cursor.execute(f"DROP TABLE {table} PURGE")
    except oracledb.DatabaseError:
        pass
cursor.execute("CREATE TABLE item (id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, name VARCHAR2(20))")
cursor.executemany("INSERT INTO item (name) VALUES (:1)", [(f"n{i}",) for i in range(50)])
conn.commit()

# paginação: 12c+ tem OFFSET/FETCH; antes só havia ROWNUM (e ainda aparece em código legado)
cursor.execute("SELECT name FROM item ORDER BY id OFFSET :o ROWS FETCH NEXT :n ROWS ONLY", o=10, n=3)
print("OFFSET/FETCH:", cursor.fetchall())
cursor.execute("""SELECT name FROM (SELECT name, ROWNUM rn FROM (SELECT name FROM item ORDER BY id) WHERE ROWNUM <= 13) WHERE rn > 10""")
print("ROWNUM (legado, 3 níveis de subconsulta):", cursor.fetchall())

# MERGE: o upsert do Oracle
cursor.execute("CREATE TABLE cnt (w VARCHAR2(10) PRIMARY KEY, n NUMBER)")
for word in "a b a c a".split():
    cursor.execute("""MERGE INTO cnt t USING (SELECT :w AS w FROM dual) s ON (t.w = s.w)
                      WHEN MATCHED THEN UPDATE SET t.n = t.n + 1
                      WHEN NOT MATCHED THEN INSERT (w, n) VALUES (s.w, 1)""", w=word)
conn.commit()
cursor.execute("SELECT w, n FROM cnt ORDER BY w")
print("MERGE:", cursor.fetchall())

# PL/SQL: funções e procedimentos armazenados
cursor.execute("CREATE OR REPLACE FUNCTION dobro(x NUMBER) RETURN NUMBER IS BEGIN RETURN x * 2; END;")
print("callfunc('dobro', 21):", cursor.callfunc("dobro", int, [21]))
cursor.execute("""CREATE OR REPLACE PROCEDURE soma(a IN NUMBER, b IN NUMBER, total OUT NUMBER) IS BEGIN total := a + b; END;""")
total = cursor.var(int)
cursor.callproc("soma", [2, 3, total])
print("callproc com parâmetro OUT:", total.getvalue())
for table in ("item", "cnt"):
    cursor.execute(f"DROP TABLE {table} PURGE")
cursor.execute("DROP FUNCTION dobro")
cursor.execute("DROP PROCEDURE soma")
conn.close()


async def main():
    async with oracledb.connect_async(**ORACLE) as aconn:           # API assíncrona nativa
        acursor = aconn.cursor()
        await acursor.execute("SELECT 'async' || ' ok' FROM dual")
        print("python-oracledb assíncrono:", await acursor.fetchone())


asyncio.run(main())
