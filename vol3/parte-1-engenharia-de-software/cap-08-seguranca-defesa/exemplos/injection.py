"""Injeção: SQL, comandos de shell, HTML. Dados nunca devem virar código."""
import html
import os
import sqlite3
import subprocess
import sys

# --- SQL ---------------------------------------------------------------------------------------------
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT, role TEXT, secret TEXT)")
conn.executemany("INSERT INTO users VALUES (?, ?, ?)", [("ana", "user", "s1"), ("bia", "admin", "s2")])

attack = "x' OR '1'='1"
unsafe_sql = f"SELECT name, secret FROM users WHERE name = '{attack}'"
print("SQL montado:", unsafe_sql)
print("  inseguro devolve:", conn.execute(unsafe_sql).fetchall())
print("  parametrizado devolve:", conn.execute("SELECT name, secret FROM users WHERE name = ?", (attack,)).fetchall())

# Parâmetros valem para VALORES; nomes de tabela/coluna precisam de lista de permissão
ALLOWED_COLUMNS = {"name", "role"}
column = "role; DROP TABLE users"
print("  coluna permitida?", column in ALLOWED_COLUMNS)

# --- Shell -------------------------------------------------------------------------------------------------
separator = "&" if os.name == "nt" else ";"
user_input = f"ola {separator} echo INJETADO"
shell_output = subprocess.run(f"echo {user_input}", shell=True, capture_output=True, text=True).stdout
print("shell=True com texto montado ->", [line.strip() for line in shell_output.splitlines() if line.strip()])
safe_output = subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1])", user_input], capture_output=True, text=True).stdout
print("lista de argumentos, sem shell ->", safe_output.strip())

# --- HTML (XSS) -------------------------------------------------------------------------------------------
comment = '<script>alert("x")</script>'
print("sem escapar:", f"<p>{comment}</p>")
print("escapado   :", f"<p>{html.escape(comment)}</p>")
