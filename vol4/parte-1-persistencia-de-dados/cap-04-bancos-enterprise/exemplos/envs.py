"""Endereços dos servidores (Capítulo 12 do Volume 3: configuração por ambiente)."""
import os

ORACLE = dict(user=os.environ.get("ORACLE_USER", "system"), password=os.environ.get("ORACLE_PASSWORD", "oracle"),
              dsn=os.environ.get("ORACLE_DSN", "localhost:51521/FREEPDB1"))
MSSQL_CS = os.environ.get("MSSQL_CS", "SERVER=localhost,51433;DATABASE={db};UID=sa;PWD=Livro_12345;Encrypt=no;TrustServerCertificate=yes")
