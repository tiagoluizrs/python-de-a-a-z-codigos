"""As pegadinhas de quem vem do PostgreSQL/SQLite. Rode nos DOIS servidores."""
import pymysql

import mysqlenv

server = mysqlenv.server_name()
print(f"=== {server} ===")
conn = mysqlenv.connect(autocommit=True)
cursor = conn.cursor()


def run(sql, params=None):
    cursor.execute(sql, params)
    return cursor.fetchall()


cursor.execute("DROP TABLE IF EXISTS t")
cursor.execute("CREATE TABLE t (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(10)) ENGINE=InnoDB")

# 1. DDL CONFIRMA a transação sozinho (commit implícito)
conn.autocommit(False)
cursor.execute("INSERT INTO t (name) VALUES ('antes')")
cursor.execute("CREATE TABLE ddl_marker (x INT)")        # <- commit implícito aqui
conn.rollback()
print("1. DDL e rollback: linhas que sobraram =", run("SELECT COUNT(*) AS n FROM t")[0]["n"], "(o rollback NÃO desfez o INSERT: o CREATE TABLE confirmou)")
cursor.execute("DROP TABLE ddl_marker")
conn.autocommit(True)

# 2. a ordenação padrão IGNORA maiúsculas e acentos
cursor.execute("CREATE TABLE u (email VARCHAR(50) UNIQUE) ENGINE=InnoDB")
cursor.execute("INSERT INTO u VALUES ('Ana@x.com')")
try:
    cursor.execute("INSERT INTO u VALUES ('ana@x.com')")
except pymysql.err.IntegrityError as error:
    print("2. UNIQUE é case-insensitive por padrão:", error.args[0], error.args[1][:40])
cursor.execute("DROP TABLE u")
cursor.execute("CREATE TABLE u (email VARCHAR(50) COLLATE utf8mb4_bin UNIQUE) ENGINE=InnoDB")
cursor.execute("INSERT INTO u VALUES ('Ana@x.com'), ('ana@x.com')")
print("   com COLLATE utf8mb4_bin as duas coexistem:", [r["email"] for r in run("SELECT email FROM u ORDER BY email")])
cursor.execute("DROP TABLE u")

# 3. modo estrito: valor grande demais é ERRO; sem o modo, é TRUNCADO em silêncio
try:
    cursor.execute("INSERT INTO t (name) VALUES (%s)", ("x" * 30,))
except pymysql.err.DataError as error:
    print("3. modo estrito:", error.args[0], "(Data too long)")
cursor.execute("SET SESSION sql_mode = ''")
cursor.execute("INSERT INTO t (name) VALUES (%s)", ("y" * 30,))
print("   sem sql_mode: gravou", len(run("SELECT name FROM t ORDER BY id DESC LIMIT 1")[0]["name"]), "caracteres de 30 (truncou, só um aviso)")
cursor.execute("SET SESSION sql_mode = DEFAULT")

# 4. utf8 NÃO é UTF-8 completo: use utf8mb4
cursor.execute("DROP TABLE IF EXISTS e")
cursor.execute("CREATE TABLE e (s VARCHAR(10)) CHARACTER SET utf8mb3")
try:
    cursor.execute("INSERT INTO e VALUES (%s)", ("ok \U0001F600",))
except pymysql.err.DataError as error:
    print("4. utf8mb3 recusou o caractere de 4 bytes: erro", error.args[0], "(Incorrect string value)")
cursor.execute("DROP TABLE e")
cursor.execute("CREATE TABLE e (s VARCHAR(10)) CHARACTER SET utf8mb4")
cursor.execute("INSERT INTO e VALUES (%s)", ("ok \U0001F600",))
print("   utf8mb4 aceita:", run("SELECT s FROM e")[0]["s"].encode("ascii", "backslashreplace").decode())
cursor.execute("DROP TABLE e")

# 5. RETURNING: só o MariaDB
try:
    cursor.execute("INSERT INTO t (name) VALUES ('r') RETURNING id")
    print("5. RETURNING funcionou:", cursor.fetchall())
except pymysql.err.ProgrammingError as error:
    print("5. RETURNING não existe neste servidor (erro", error.args[0], "): use cursor.lastrowid")

# 6. UPSERT e INSERT IGNORE
cursor.execute("CREATE TABLE c (w VARCHAR(10) PRIMARY KEY, n INT) ENGINE=InnoDB")
for word in "a b a c a".split():
    cursor.execute("INSERT INTO c VALUES (%s, 1) ON DUPLICATE KEY UPDATE n = n + 1", (word,))
print("6. ON DUPLICATE KEY UPDATE:", run("SELECT w, n FROM c ORDER BY w"))
cursor.execute("INSERT IGNORE INTO c VALUES ('a', 99)")
print("   INSERT IGNORE ignorou o duplicado (rowcount", cursor.rowcount, ") - mas também ignora OUTROS erros: cuidado")

# 7. JSON
cursor.execute("DROP TABLE IF EXISTS j")
cursor.execute("CREATE TABLE j (doc JSON)")
cursor.execute("INSERT INTO j VALUES (%s)", ('{"a": {"b": [1, 2, 3]}}',))
print("7. JSON_EXTRACT:", run("SELECT JSON_EXTRACT(doc, '$.a.b[1]') AS v FROM j"), "| no Python o JSON chega como", type(run("SELECT doc FROM j")[0]["doc"]).__name__)

for table in ("t", "c", "j"):
    cursor.execute(f"DROP TABLE {table}")
conn.close()
