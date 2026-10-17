"""Loggers formam uma árvore pelo nome; o nível e os handlers são herdados."""
import logging
import subprocess
import sys

print(logging.getLevelNamesMapping())

app = logging.getLogger("app")
db = logging.getLogger("app.db")
print(db.parent is app, app.parent is logging.getLogger(), logging.getLogger("app.db") is db)
print("nível próprio:", db.level, "| efetivo:", db.getEffectiveLevel())          # NOTSET herda do pai até a raiz
app.setLevel(logging.DEBUG)
print("depois de app.setLevel(DEBUG):", db.getEffectiveLevel())

# O nível do logger decide se o registro nasce; o do handler, se ele é emitido
CODE = """
import logging
log = logging.getLogger("lib.sub")
log.info("info: descartada")
log.warning("warning: aparece mesmo sem configuração")
print("handlers do logger:", log.handlers, "| raiz:", logging.getLogger().handlers)
print("lastResort:", logging.lastResort)
"""
result = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True)
print("--- stdout:\n" + result.stdout.strip())
print("--- stderr:\n" + result.stderr.strip())

# propagate: o registro sobe pelos pais, passando pelos HANDLERS deles (não pelos níveis)
import io

buf_parent, buf_child = io.StringIO(), io.StringIO()
parent = logging.getLogger("svc")
child = logging.getLogger("svc.worker")
parent.setLevel(logging.INFO)
parent.addHandler(logging.StreamHandler(buf_parent))
child.addHandler(logging.StreamHandler(buf_child))
child.setLevel(logging.INFO)
child.info("a")
child.propagate = False
child.info("b")
print("pai recebeu:", buf_parent.getvalue().split(), "| filho recebeu:", buf_child.getvalue().split())
