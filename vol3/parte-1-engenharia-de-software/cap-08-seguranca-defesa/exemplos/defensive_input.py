"""Validar na fronteira: lista de permissão, limites, assert que some e arquivos temporários."""
import os
import stat
import subprocess
import sys
import tempfile
from decimal import Decimal, InvalidOperation

# --- assert não é validação: sob -O ele desaparece (Capítulo 7 do Volume 2) ----------------------------------------------
code = """
def withdraw(balance, amount):
    assert amount > 0, "valor inválido"
    return balance - amount
print(withdraw(100, -50))
"""
for flags in ([], ["-O"]):
    result = subprocess.run([sys.executable, *flags, "-c", code], capture_output=True, text=True)
    print(f"python {' '.join(flags):<3}->", (result.stdout.strip() or result.stderr.strip().splitlines()[-1]))


def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("valor inválido")                  # if + raise: nunca é removido
    return balance - amount


# --- Lista de permissão (allowlist), não de proibição ---------------------------------------------------------------
ALLOWED_SORT = {"name", "created", "price"}


def sort_column(requested):
    if requested not in ALLOWED_SORT:
        raise ValueError(f"coluna não permitida: {requested!r}")
    return requested


print(sort_column("price"))
try:
    sort_column("price; DROP TABLE x")
except ValueError as error:
    print("recusado:", error)

# --- Dinheiro e números: Decimal, faixas e tamanhos ---------------------------------------------------------------------
def parse_amount(text, *, maximum=Decimal("1000000")):
    if len(text) > 20:
        raise ValueError("texto longo demais")
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise ValueError(f"não é um número: {text!r}") from None
    if not value.is_finite() or not Decimal(0) < value <= maximum:
        raise ValueError("fora da faixa")
    return value


for text in ("19.90", "NaN", "-5", "1e999", "abc"):
    try:
        print(f"{text!r:>8} ->", parse_amount(text))
    except ValueError as error:
        print(f"{text!r:>8} -> ValueError: {error}")

# --- Arquivos temporários e permissões ------------------------------------------------------------------------------------
handle, path = tempfile.mkstemp()                           # cria de forma atômica, com permissão 0600
os.close(handle)
mode = stat.S_IMODE(os.stat(path).st_mode)
print("mkstemp: permissões", oct(mode), "(no Windows o modo é aproximado)")
os.remove(path)
print("tempfile.mktemp existe só por compatibilidade (corrida entre nomear e criar):", hasattr(tempfile, "mktemp"))
