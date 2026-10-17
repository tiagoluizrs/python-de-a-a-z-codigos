"""Handlers, níveis por handler, filtros e rotação de arquivos."""
import io
import logging
import logging.handlers
import os
import tempfile

logger = logging.getLogger("handlers.demo")
logger.setLevel(logging.DEBUG)
logger.propagate = False

console, details = io.StringIO(), io.StringIO()
h_console = logging.StreamHandler(console)
h_console.setLevel(logging.WARNING)                              # console: só avisos e erros
h_console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
h_details = logging.StreamHandler(details)                       # "arquivo": tudo, com mais contexto
h_details.setFormatter(logging.Formatter("%(levelname)s %(name)s %(funcName)s: %(message)s"))
logger.addHandler(h_console)
logger.addHandler(h_details)

logger.debug("detalhe")
logger.warning("aviso")
logger.error("erro")
print("console:", console.getvalue().split("\n")[:-1])
print("detalhes:", details.getvalue().count("\n"), "linhas")


# Filtro: decide se o registro passa (e pode alterá-lo)
class OnlyInfo(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


info_only = io.StringIO()
h_info = logging.StreamHandler(info_only)
h_info.addFilter(OnlyInfo())
logger.addHandler(h_info)
logger.info("passa")
logger.warning("não passa neste handler")
print("só INFO:", info_only.getvalue().split())

# Rotação por tamanho
folder = tempfile.mkdtemp()
path = os.path.join(folder, "app.log")
rotating = logging.handlers.RotatingFileHandler(path, maxBytes=200, backupCount=2, encoding="utf-8")
rot_logger = logging.getLogger("handlers.rot")
rot_logger.setLevel(logging.INFO)
rot_logger.propagate = False
rot_logger.addHandler(rotating)
for i in range(60):
    rot_logger.info("mensagem numero %02d", i)
rotating.close()
files = sorted(os.listdir(folder))
print("arquivos:", files, "| tamanhos:", [os.path.getsize(os.path.join(folder, f)) for f in files])
with open(os.path.join(folder, "app.log.2"), encoding="utf-8") as handle:
    print("o arquivo mais antigo começa em:", handle.readline().strip())

print("tipos de handler:", [n for n in dir(logging.handlers) if n.endswith("Handler")])
