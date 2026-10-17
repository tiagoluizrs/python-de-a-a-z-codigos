"""python arquivo.py x python -m pacote: quem é o __main__."""
import subprocess
import sys

CODE = "import inventory, sys; print(__name__, '|', inventory.__name__, '|', sys.argv[1:])"
print(subprocess.run([sys.executable, "-c", CODE, "a", "b"], capture_output=True, text=True).stdout.strip())

result = subprocess.run([sys.executable, "-m", "inventory", "--version"], capture_output=True, text=True)
print("python -m inventory --version ->", result.stdout.strip())

result = subprocess.run([sys.executable, "-m", "inventory", "--file", "x.json"], capture_output=True, text=True)
print("sem subcomando -> código de saída", result.returncode)

# Rodar um arquivo DENTRO do pacote como script quebra os imports relativos
import inventory
from pathlib import Path

cli_file = Path(inventory.__file__).with_name("cli.py")
result = subprocess.run([sys.executable, str(cli_file)], capture_output=True, text=True)
print("python .../cli.py ->", result.stderr.strip().splitlines()[-1])
