"""Variáveis de ambiente: ler, converter (tudo é texto!) e herdar."""
import os
import subprocess
import sys

os.environ["DEMO_PORT"] = "8080"
os.environ["DEMO_DEBUG"] = "false"
os.environ["DEMO_HOSTS"] = "a.example.com, b.example.com ,c.example.com"

print("os.environ[...]    :", os.environ["DEMO_PORT"], type(os.environ["DEMO_PORT"]).__name__)
print("os.getenv ausente  :", os.getenv("DEMO_MISSING"), "| com padrão:", os.getenv("DEMO_MISSING", "padrão"))
try:
    os.environ["DEMO_MISSING"]
except KeyError as error:
    print("os.environ ausente : KeyError", error)

# Tudo é str: a armadilha clássica
print("\nbool('false') ->", bool(os.environ["DEMO_DEBUG"]), "(texto não vazio é verdadeiro!)")


def as_bool(text):
    value = text.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off", ""}:
        return False
    raise ValueError(f"booleano inválido: {text!r}")


print("as_bool('false') ->", as_bool(os.environ["DEMO_DEBUG"]))
print("lista:", [h.strip() for h in os.environ["DEMO_HOSTS"].split(",")])
print("porta + 1 sem converter falha:", end=" ")
try:
    os.environ["DEMO_PORT"] + 1
except TypeError as error:
    print("TypeError:", error)

# Valores só podem ser texto
try:
    os.environ["DEMO_NUM"] = 5
except TypeError as error:
    print("os.environ['X'] = 5 ->", "TypeError:", error)

# Herança: o processo filho recebe uma CÓPIA do ambiente (e vê os segredos)
child = subprocess.run([sys.executable, "-c", "import os; print(os.environ.get('DEMO_PORT'))"], capture_output=True, text=True)
print("\nfilho vê DEMO_PORT:", child.stdout.strip())
clean = {k: v for k, v in os.environ.items() if not k.startswith("DEMO_")}
child = subprocess.run([sys.executable, "-c", "import os; print(os.environ.get('DEMO_PORT'))"], capture_output=True, text=True, env=clean)
print("filho com ambiente filtrado:", child.stdout.strip())

# Windows: nomes sem diferenciar maiúsculas; Linux e macOS diferenciam
print("\nPATH e path são a mesma variável?", os.environ.get("PATH") == os.environ.get("path"), f"(sistema: {os.name})")

# Modo UTF-8 padrão no 3.15 (PEP 686): afeta open() sem encoding
flags = subprocess.run([sys.executable, "-c", "import sys; print(sys.flags.utf8_mode)"], capture_output=True, text=True).stdout.strip()
off = subprocess.run([sys.executable, "-c", "import sys; print(sys.flags.utf8_mode)"], capture_output=True, text=True, env={**os.environ, "PYTHONUTF8": "0"}).stdout.strip()
print("utf8_mode padrão:", flags, "| com PYTHONUTF8=0:", off)
