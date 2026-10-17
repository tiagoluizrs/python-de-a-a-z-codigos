"""Dois drivers (PyMySQL e mysql-connector), tipos, configuração dos servidores."""
import datetime as dt
import decimal
from importlib.metadata import version

import mysql.connector

import mysqlenv

server = mysqlenv.server_name()
host, port = mysqlenv.SERVERS[server]
print(f"servidor: {server} ({host}:{port}) | PyMySQL {version("pymysql")} | mysql-connector {version("mysql-connector-python")}")

with mysqlenv.connect() as conn:                                     # PyMySQL: o with FECHA a conexão
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION() AS version, @@character_set_server AS charset, @@collation_server AS collation, "
                       "@@transaction_isolation AS isolation, @@autocommit AS autocommit")
        print("configuração:", cursor.fetchone())
        cursor.execute("DROP TABLE IF EXISTS demo")
        cursor.execute("CREATE TABLE demo (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) NOT NULL, "
                       "price DECIMAL(10, 2), at DATETIME, meta JSON) ENGINE=InnoDB")
        cursor.execute("INSERT INTO demo (name, price, at, meta) VALUES (%s, %s, %s, %s)",
                       ("caneta", decimal.Decimal("9.90"), dt.datetime(2026, 10, 7, 9, 30), '{"cor": "azul"}'))
        print("lastrowid:", cursor.lastrowid, "| rowcount:", cursor.rowcount)
        conn.commit()                                                # autocommit vem DESLIGADO: sem commit o dado some
        cursor.execute("SELECT * FROM demo")
        row = cursor.fetchone()
        print("tipos:", {key: type(value).__name__ for key, value in row.items()})
        print("DECIMAL vira Decimal:", row["price"], "| DATETIME vem SEM fuso:", row["at"].tzinfo, "| JSON vem como", type(row["meta"]).__name__)
        cursor.execute("DROP TABLE demo")
    conn.commit()

# o mesmo, com o driver oficial da Oracle
connection = mysql.connector.connect(host=host, port=port, user="root", password="root", database="livro")
cursor = connection.cursor(dictionary=True)
cursor.execute("SELECT 1 + 1 AS two")
print("mysql-connector:", cursor.fetchone(), "| autocommit padrão:", connection.autocommit)
cursor.close()
connection.close()
print("placeholder dos DOIS drivers é %s (não ?). Valores SEMPRE por parâmetro (Capítulo 8 do Volume 3).")
