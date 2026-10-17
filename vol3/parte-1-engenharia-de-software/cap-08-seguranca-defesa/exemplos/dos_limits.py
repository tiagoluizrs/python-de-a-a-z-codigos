"""Negação de serviço: regex catastrófica, números enormes, hashes e arquivos gigantes."""
import os
import re
import subprocess
import sys
import time

# --- ReDoS: um padrão com repetição aninhada explode em entradas "quase certas" --------------------------
pattern = re.compile(r"^(a+)+$")
safe = re.compile(r"^a+$")
print("n   padrão (a+)+$   padrão a+$")
for n in (16, 20, 22, 24):
    text = "a" * n + "b"
    start = time.perf_counter()
    pattern.match(text)
    bad = time.perf_counter() - start
    start = time.perf_counter()
    safe.match(text)
    good = time.perf_counter() - start
    print(f"{n:<4}{bad:>10.3f} s   {good * 1e6:>10.1f} us")

# --- Limite de dígitos na conversão de texto para int (desde o 3.11) ----------------------------------------
print("limite padrão:", sys.get_int_max_str_digits())
try:
    int("9" * 5000)
except ValueError as error:
    print("ValueError:", str(error)[:60])

# --- Hash de texto aleatorizado: defesa contra colisões forçadas ----------------------------------------------
def hash_in_new_process(seed=None):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONHASHSEED"}
    if seed is not None:
        env["PYTHONHASHSEED"] = seed
    return subprocess.run([sys.executable, "-c", "print(hash('abc'))"], capture_output=True, text=True, env=env).stdout.strip()


print("hash('abc') em dois processos:", hash_in_new_process(), hash_in_new_process())
print("com PYTHONHASHSEED=0 (reprodutível):", hash_in_new_process("0") == hash_in_new_process("0"))

# --- Ler sem limite: um arquivo (ou requisição) gigante esgota a memória -------------------------------------------
MAX = 1_000
import io

stream = io.BytesIO(b"x" * 10_000)
chunk = stream.read(MAX + 1)
print("leitura limitada a", MAX, "bytes ->", "excede o limite" if len(chunk) > MAX else "ok")
