"""Configuração comum: qual servidor usar (``python exemplo.py mysql|mariadb``)."""
import os
import sys

import pymysql
from pymysql.cursors import DictCursor

SERVERS = {
    "mysql": (os.environ.get("MYSQL_HOST", "127.0.0.1"), int(os.environ.get("MYSQL_PORT", "53306"))),
    "mariadb": (os.environ.get("MARIADB_HOST", "127.0.0.1"), int(os.environ.get("MARIADB_PORT", "53307"))),
}


def server_name():
    return sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in SERVERS else "mysql"


def connect(server=None, **kwargs):
    host, port = SERVERS[server or server_name()]
    kwargs.setdefault("cursorclass", DictCursor)
    kwargs.setdefault("charset", "utf8mb4")
    return pymysql.connect(host=host, port=port, user="root", password="root", database="livro", **kwargs)
