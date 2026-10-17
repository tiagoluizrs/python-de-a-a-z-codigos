"""Import circular: o erro e duas formas de resolver."""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent / "circular"


def attempt(folder: str, code: str) -> None:
    env = {**os.environ, "PYTHONPATH": str(HERE / folder)}
    out = subprocess.run([sys.executable, "-c", code], env=env,
                         cwd=HERE, capture_output=True, text=True)
    text = (out.stdout + out.stderr).strip().splitlines()
    print(f"[{folder}]", text[-1][:112] if text else "(ok)")


attempt("bad", "import orders")
attempt("fixed_local",
        "import customers; print(customers.Customer('Ana').new_order().customer.name)")
attempt("fixed_split",
        "import types_; print(types_.Customer('Ana'))")

# Por dentro: no ciclo, o modulo 'customers' esta em sys.modules mas
# ainda NAO terminou de executar (esta parcialmente inicializado).
