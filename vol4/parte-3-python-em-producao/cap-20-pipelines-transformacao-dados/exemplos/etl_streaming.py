"""Um ETL em fluxo: extrair -> validar -> transformar -> carregar, com memória limitada e quarentena dos registros ruins."""
import csv
import itertools
import os
import sqlite3
import tempfile
import time
import tracemalloc
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path

import psutil

from gen_data import make_csv

work = Path(tempfile.mkdtemp(prefix="etl-"))
N = 1_000_000
t0 = time.perf_counter()
source = make_csv(work / "events.csv", N, dirty=0.02)
print(f"fonte: {N:,} linhas, {os.path.getsize(source) / 1e6:.0f} MB (gerada em {time.perf_counter() - t0:.1f} s), 2% de linhas ruins\n")

COUNTRY_FIX = {"br": "BR", "Brasil": "BR"}


class Rejected(Exception):
    pass


# ---------- extrair: um GERADOR (uma linha de cada vez, nunca o arquivo inteiro) ----------
def extract(path: Path) -> Iterator[tuple[int, list[str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)                                              # cabeçalho
        for line_number, row in enumerate(reader, start=2):
            yield line_number, row


# ---------- transformar: cada linha vira um registro tipado, ou é REJEITADA com o motivo ----------
def parse(line_number: int, row: list[str]) -> dict:
    if len(row) != 7:
        raise Rejected("colunas")
    event_id, user_id, ts, product, qty, price, country = row
    if not user_id:
        raise Rejected("user_id vazio")
    try:
        stamp = datetime.fromisoformat(ts)
        qty_i, price_f = int(qty), float(price)
    except ValueError:
        raise Rejected("data ou número inválido") from None
    if qty_i <= 0:
        raise Rejected("quantidade não positiva")
    return {"event_id": int(event_id), "user_id": int(user_id), "ts": stamp.isoformat(), "product": product, "qty": qty_i,
            "total": round(qty_i * price_f, 2), "country": COUNTRY_FIX.get(country, country)}


def transform(rows: Iterable[tuple[int, list[str]]], rejects: list) -> Iterator[dict]:
    seen: set[int] = set()
    for line_number, row in rows:
        try:
            record = parse(line_number, row)
            if record["event_id"] in seen:
                raise Rejected("event_id duplicado")
            seen.add(record["event_id"])
        except Rejected as reason:
            rejects.append((line_number, str(reason)))
            continue
        yield record


# ---------- carregar: em LOTES ----------
def batched(iterable: Iterable, size: int) -> Iterator[list]:
    it = iter(iterable)
    while batch := list(itertools.islice(it, size)):
        yield batch


def load(records: Iterable[dict], db: sqlite3.Connection, batch_size: int = 10_000) -> int:
    total = 0
    for batch in batched(records, batch_size):
        with db:
            db.executemany("insert into events values (:event_id, :user_id, :ts, :product, :qty, :total, :country)", batch)
        total += len(batch)
    return total


def make_db(path=":memory:") -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("create table events (event_id integer primary key, user_id integer, ts text, product text, qty integer, total real, country text)")
    return db


# 1. o pipeline em fluxo: o tempo, e DEPOIS a memória (o tracemalloc deixa tudo ~10x mais lento: nunca meça tempo com ele ligado)
def run_stream(path_db):
    rejects: list[tuple[int, str]] = []
    db = make_db(path_db)
    loaded = load(transform(extract(source), rejects), db)
    return loaded, rejects


start = time.perf_counter()
loaded, rejects = run_stream(str(work / "target.db"))
elapsed = time.perf_counter() - start
print(f"EM FLUXO: {loaded:,} carregadas, {len(rejects):,} rejeitadas em {elapsed:.1f} s ({N / elapsed:,.0f} linhas/s)")
tracemalloc.start()
run_stream(":memory:")
peak_py = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
print(f"  pico de memória do Python (medido à parte, com tracemalloc): {peak_py / 1e6:.0f} MB, dos quais o conjunto de event_id para achar duplicatas é o maior")
from collections import Counter

print("  motivos das rejeições:", dict(Counter(reason for _, reason in rejects)))

# 2. a quarentena: o que foi rejeitado vai para um arquivo, com o NÚMERO DA LINHA e o motivo, para alguém olhar
quarantine = work / "rejects.csv"
with quarantine.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["line", "reason"])
    writer.writerows(rejects)
print(f"  quarentena: {quarantine.name} com {len(rejects):,} linhas | exemplo: {rejects[:2]}")
print(f"  conferência: carregadas + rejeitadas = {loaded + len(rejects):,} == linhas da fonte ({N:,})? {loaded + len(rejects) == N}")

# 3. a versão "carrega tudo na memória": mesma lógica, listas em vez de geradores
start = time.perf_counter()
rows = list(extract(source))
records = list(transform(rows, []))
elapsed_all = time.perf_counter() - start
del rows, records
tracemalloc.start()
rows = list(extract(source))
records = list(transform(rows, []))
peak_all = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
del rows, records
print(f"\nEM LISTAS (tudo na memória, sem carregar): {elapsed_all:.1f} s | pico de memória: {peak_all / 1e6:.0f} MB ({peak_all / peak_py:.0f}x o do fluxo)")

# 4. o tamanho do lote na carga
print("\ncarga no SQLite (200.000 registros) por tamanho de lote:")
sample = list(itertools.islice(transform(extract(source), []), 200_000))
for size in (1, 100, 10_000, 200_000):
    db2 = make_db()
    start = time.perf_counter()
    n = size if size < 200_000 else 200_000
    if size == 1:
        for record in sample[:20_000]:                             # uma transação por linha: 20.000 bastam para medir
            with db2:
                db2.execute("insert into events values (:event_id, :user_id, :ts, :product, :qty, :total, :country)", record)
        rate = 20_000 / (time.perf_counter() - start)
    else:
        load(sample, db2, batch_size=size)
        rate = len(sample) / (time.perf_counter() - start)
    print(f"  lote de {size:>7,}: {rate:>10,.0f} linhas/s")

# 5. onde o tempo vai: extrair, transformar, carregar (cada etapa isolada)
start = time.perf_counter()
n_rows = sum(1 for _ in extract(source))
t_extract = time.perf_counter() - start
start = time.perf_counter()
n_ok = sum(1 for _ in transform(extract(source), []))
t_transform = time.perf_counter() - start - t_extract
print(f"\netapas (1M linhas): extrair {t_extract:.1f} s | validar e transformar {t_transform:.1f} s | carregar {elapsed - t_extract - t_transform:.1f} s")
