"""Direcionar avisos e exceções não tratadas para o logging."""
import io
import logging
import subprocess
import sys
import warnings

buf = io.StringIO()
handler = logging.StreamHandler(buf)
handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
logging.getLogger("py.warnings").addHandler(handler)
logging.getLogger("py.warnings").propagate = False

logging.captureWarnings(True)
warnings.warn("função antiga", DeprecationWarning, stacklevel=1)
logging.captureWarnings(False)
print(buf.getvalue().splitlines()[0][:70])

# Exceção não tratada: registrar antes de morrer
CODE = """
import logging, sys
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def hook(exc_type, exc, tb):
    logging.critical("exceção não tratada", exc_info=(exc_type, exc, tb))

sys.excepthook = hook
raise RuntimeError("explodiu")
"""
result = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True)
lines = result.stderr.strip().splitlines()
print("código de saída:", result.returncode, "|", lines[0], "|", lines[-1])
