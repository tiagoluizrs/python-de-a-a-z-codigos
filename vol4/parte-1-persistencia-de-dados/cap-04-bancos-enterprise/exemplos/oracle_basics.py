"""Oracle com python-oracledb (modo thin: Python puro, sem instalar o cliente Oracle)."""
import datetime as dt
import decimal

import oracledb

from envs import ORACLE

print("python-oracledb", oracledb.__version__, "| modo thin:", oracledb.is_thin_mode())

with oracledb.connect(**ORACLE) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT banner_full FROM v$version")
    print(cursor.fetchone()[0].splitlines()[0])
    cursor.execute("SELECT 1 + 1 FROM dual")                # DUAL: a tabela de uma linha para expressões
    print("FROM dual:", cursor.fetchone())

    for table in ("demo",):
        try:
            cursor.execute(f"DROP TABLE {table} PURGE")
        except oracledb.DatabaseError:
            pass
    cursor.execute("""CREATE TABLE demo (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name VARCHAR2(50) NOT NULL, price NUMBER(10, 2), at DATE)""")

    # binds nomeados (:nome) ou posicionais (:1); RETURNING ... INTO devolve a chave gerada
    new_id = cursor.var(int)
    cursor.execute("INSERT INTO demo (name, price, at) VALUES (:n, :p, :a) RETURNING id INTO :new_id",
                   n="caneta", p=decimal.Decimal("9.90"), a=dt.datetime(2026, 10, 7, 9, 30), new_id=new_id)
    print("RETURNING INTO:", new_id.getvalue())
    conn.commit()

    cursor.execute("SELECT price, at, id FROM demo")
    row = cursor.fetchone()
    print("tipos:", [type(value).__name__ for value in row], row)
    print("  NUMBER(10,2) chegou como float! Para Decimal: oracledb.defaults.fetch_decimals = True")
    oracledb.defaults.fetch_decimals = True
    cursor.execute("SELECT price FROM demo")
    print("  com fetch_decimals:", repr(cursor.fetchone()[0]))
    oracledb.defaults.fetch_decimals = False
    print("  DATE do Oracle TEM hora:", row[1], "(não é só data)")

    # o Oracle trata string vazia como NULL
    try:
        cursor.execute("INSERT INTO demo (name) VALUES (:1)", [""])
    except oracledb.IntegrityError as error:
        print("string vazia = NULL:", str(error).splitlines()[0])

    # nomes não citados viram MAIÚSCULAS
    cursor.execute("SELECT table_name, column_name FROM user_tab_columns WHERE table_name = 'DEMO' ORDER BY column_id")
    print("dicionário de dados em maiúsculas:", cursor.fetchall()[:3])
    print("cursor.description usa MAIÚSCULAS:", [column[0] for column in cursor.execute("SELECT * FROM demo").description])

    # DDL confirma a transação (como no MySQL)
    cursor.execute("INSERT INTO demo (name) VALUES ('antes')")
    cursor.execute("CREATE TABLE ddl_marker (x NUMBER)")
    conn.rollback()
    cursor.execute("SELECT COUNT(*) FROM demo WHERE name = 'antes'")
    print("DDL e rollback: linhas 'antes' =", cursor.fetchone()[0], "(o CREATE TABLE confirmou o INSERT)")
    cursor.execute("DROP TABLE ddl_marker PURGE")
    cursor.execute("DROP TABLE demo PURGE")
