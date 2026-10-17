"""Cargas IDEMPOTENTES e INCREMENTAIS: rodar duas vezes não duplica, e rodar de novo só busca o que mudou."""
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path


def make_target() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.execute("create table sales (order_id integer, day text, total real, updated_at text)")
    return db


SOURCE_DAY1 = [(1, "2026-03-01", 100.0, "2026-03-01T10:00"), (2, "2026-03-01", 50.0, "2026-03-01T11:00"), (3, "2026-03-01", 25.0, "2026-03-01T12:00")]

# 1. a carga INGÊNUA: um INSERT. Reexecutar (um retry, um backfill, um erro do agendador) DUPLICA
db = make_target()
for _ in range(2):
    db.executemany("insert into sales values (?, ?, ?, ?)", SOURCE_DAY1)
rows, total = db.execute("select count(*), sum(total) from sales").fetchone()
print(f"INSERT ingênuo, rodado 2 vezes: {rows} linhas (eram 3), receita {total} (era 175.0): a receita DOBROU")

# 2. com chave primária, a reexecução FALHA (melhor que duplicar em silêncio, mas ainda quebra o pipeline)
db = sqlite3.connect(":memory:")
db.execute("create table sales (order_id integer primary key, day text, total real, updated_at text)")
db.executemany("insert into sales values (?, ?, ?, ?)", SOURCE_DAY1)
try:
    db.executemany("insert into sales values (?, ?, ?, ?)", SOURCE_DAY1)
except sqlite3.IntegrityError as error:
    print("com chave primária: a 2ª execução falha ->", error)

# 3. upsert: INSERT ... ON CONFLICT DO UPDATE: insere o novo e ATUALIZA o existente (a correção na origem chega)
db = sqlite3.connect(":memory:")
db.execute("create table sales (order_id integer primary key, day text, total real, updated_at text)")
UPSERT = """
insert into sales values (:order_id, :day, :total, :updated_at)
on conflict (order_id) do update set day = excluded.day, total = excluded.total, updated_at = excluded.updated_at
where excluded.updated_at > sales.updated_at
"""
as_dicts = lambda rows: [dict(zip(("order_id", "day", "total", "updated_at"), r)) for r in rows]
for run in (1, 2):
    db.executemany(UPSERT, as_dicts(SOURCE_DAY1))
print(f"upsert, rodado 2 vezes: {db.execute('select count(*), sum(total) from sales').fetchone()} (estável)")
corrected = [(2, "2026-03-01", 80.0, "2026-03-02T09:00")]                    # a origem corrigiu o pedido 2
db.executemany(UPSERT, as_dicts(corrected))
stale = [(2, "2026-03-01", 999.0, "2026-03-01T08:00")]                       # chega uma versão ANTIGA (fora de ordem)
db.executemany(UPSERT, as_dicts(stale))
print(f"após a correção (80) e uma versão atrasada (999, mais velha): pedido 2 = {db.execute('select total from sales where order_id = 2').fetchone()[0]} (a cláusula WHERE protege contra dados fora de ordem)")

# 4. sobrescrita de PARTIÇÃO: apaga o dia e insere de novo, em UMA transação (o padrão dos pipelines diários)
db = sqlite3.connect(":memory:")
db.execute("create table sales (order_id integer, day text, total real)")


def load_partition(db, day, rows):
    with db:                                                         # tudo ou nada: o leitor nunca vê o dia pela metade
        db.execute("delete from sales where day = ?", (day,))
        db.executemany("insert into sales values (?, ?, ?)", [(i, d, t) for i, d, t, _ in rows])


load_partition(db, "2026-03-01", SOURCE_DAY1)
load_partition(db, "2026-03-01", SOURCE_DAY1)
load_partition(db, "2026-03-02", [(4, "2026-03-02", 10.0, "x")])
print(f"sobrescrita de partição: {db.execute('select day, count(*), sum(total) from sales group by day order by day').fetchall()} (o mesmo dia 2 vezes: sem duplicar; dias diferentes: independentes)")

# 5. extração INCREMENTAL com marca d'água (watermark): só o que mudou desde a última vez
class Source:
    """Uma 'API' que devolve registros com ``updated_at`` maior que o pedido; um registro chega ATRASADO (updated_at antigo)."""

    def __init__(self):
        self.rows = {i: (i, "2026-03-01", float(i * 10), f"2026-03-01T{8 + i:02d}:00") for i in range(1, 6)}
        self.calls = 0

    def fetch(self, since: str):
        self.calls += 1
        return [r for r in self.rows.values() if r[3] > since]


state_file = Path(tempfile.mkdtemp()) / "watermark.json"


def read_watermark(default="1970-01-01T00:00") -> str:
    return json.loads(state_file.read_text())["watermark"] if state_file.exists() else default


def save_watermark(value: str) -> None:
    tmp = state_file.with_suffix(".tmp")
    tmp.write_text(json.dumps({"watermark": value}))
    os.replace(tmp, state_file)                                      # troca atômica: nunca um arquivo pela metade


def incremental_run(source, db, overlap_minutes=0) -> tuple[int, str]:
    since = read_watermark()
    if overlap_minutes:                                              # relê uma janela anterior para pegar registros atrasados
        since = (datetime.fromisoformat(since) - timedelta(minutes=overlap_minutes)).isoformat(timespec="minutes")
    rows = source.fetch(since)
    db.executemany(UPSERT, as_dicts(rows))                          # idempotente: reler a janela não duplica
    if rows:
        save_watermark(max(r[3] for r in rows))
    return len(rows), read_watermark()


db = sqlite3.connect(":memory:")
db.execute("create table sales (order_id integer primary key, day text, total real, updated_at text)")
src = Source()
print("\nextração incremental (marca d'água em arquivo):")
print("  rodada 1 (tudo):", incremental_run(src, db))
print("  rodada 2 (nada mudou):", incremental_run(src, db), "-> busca 0 linhas em vez de reler tudo")
src.rows[6] = (6, "2026-03-02", 60.0, "2026-03-02T09:00")
src.rows[2] = (2, "2026-03-01", 22.0, "2026-03-02T10:00")
print("  rodada 3 (1 novo, 1 corrigido):", incremental_run(src, db))
src.rows[7] = (7, "2026-03-02", 70.0, "2026-03-02T09:30")           # chegou DEPOIS, mas com updated_at ANTERIOR à marca d'água (10:00)
print("  rodada 4 (registro atrasado, sem sobreposição):", incremental_run(src, db), "| pedido 7 no destino?", db.execute("select count(*) from sales where order_id = 7").fetchone()[0] == 1, "(PERDIDO para sempre)")
print("  rodada 5 (com sobreposição de 60 min):", incremental_run(src, db, overlap_minutes=60), "| pedido 7 no destino?", db.execute("select count(*) from sales where order_id = 7").fetchone()[0] == 1)
print(f"  destino final: {db.execute('select count(*), sum(total) from sales').fetchone()} | chamadas à origem: {src.calls}")

# 6. a regra: toda etapa que ESCREVE deve poder rodar de novo sem mudar o resultado
print("\nregra de ouro: rode o pipeline duas vezes seguidas; se o resultado mudar, ele não é idempotente")
