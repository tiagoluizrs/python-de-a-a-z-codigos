"""Qualidade de dados como código: expectativas, relatório, quarentena e um portão que interrompe o pipeline."""
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import polars as pl

from gen_data import make_csv

work = Path(tempfile.mkdtemp(prefix="dq-"))
N = 500_000
source = make_csv(work / "events.csv", N, dirty=0.03)
raw = pl.read_csv(source, infer_schema=False)                         # tudo texto: a validação decide os tipos
print(f"{raw.height:,} linhas lidas como texto\n")


@dataclass(frozen=True)
class Check:
    name: str
    bad: pl.Expr                       # expressão que é True nas linhas RUINS
    severity: str = "error"            # "error" bloqueia; "warn" só avisa
    max_bad_ratio: float = 0.0         # fração tolerada de linhas ruins


CHECKS = [
    Check("event_id presente", pl.col("event_id").is_null() | (pl.col("event_id") == "")),
    Check("user_id presente", pl.col("user_id").is_null() | (pl.col("user_id") == ""), max_bad_ratio=0.01),
    Check("qty é inteiro positivo", pl.col("qty").cast(pl.Int64, strict=False).is_null() | (pl.col("qty").cast(pl.Int64, strict=False) <= 0), max_bad_ratio=0.01),
    Check("price é número positivo", pl.col("price").cast(pl.Float64, strict=False).is_null() | (pl.col("price").cast(pl.Float64, strict=False) <= 0), max_bad_ratio=0.01),
    Check("ts é data ISO", pl.col("ts").str.to_datetime("%Y-%m-%dT%H:%M:%S", strict=False).is_null(), max_bad_ratio=0.01),
    Check("country conhecido", ~pl.col("country").is_in(["BR", "br", "Brasil", "AR", "CL", "US", "PT"]), severity="warn"),
    Check("event_id único", pl.col("event_id").is_duplicated(), max_bad_ratio=0.005),
]


def run_checks(df: pl.DataFrame, checks: list[Check]) -> pl.DataFrame:
    # TODAS as verificações em UMA passada (Polars avalia as expressões em paralelo)
    counts = df.select([c.bad.sum().alias(c.name) for c in checks]).row(0, named=True)
    rows = []
    for check in checks:
        bad = counts[check.name]
        ratio = bad / df.height
        status = "ok" if ratio <= check.max_bad_ratio else ("FALHA" if check.severity == "error" else "aviso")
        rows.append({"verificação": check.name, "linhas ruins": bad, "fração": round(ratio, 5), "tolerância": check.max_bad_ratio, "status": status})
    return pl.DataFrame(rows)


start = time.perf_counter()
report = run_checks(raw, CHECKS)
print(f"relatório de qualidade ({(time.perf_counter() - start) * 1e3:.0f} ms para {len(CHECKS)} verificações em {N:,} linhas):")
with pl.Config(tbl_rows=20, tbl_width_chars=120, tbl_hide_dataframe_shape=True):
    print(report)


# 2. o portão: o pipeline para quando uma verificação de nível "error" estoura a tolerância
class DataQualityError(Exception):
    pass


def gate(report: pl.DataFrame) -> None:
    failed = report.filter(pl.col("status") == "FALHA")
    if failed.height:
        raise DataQualityError("; ".join(f"{r['verificação']}: {r['fração']:.2%} > {r['tolerância']:.2%}" for r in failed.iter_rows(named=True)))


try:
    gate(report)
    print("\nportão: passou")
except DataQualityError as error:
    print("\nportão: o pipeline PARA ->", error)

# 3. a quarentena: separar o que presta do que não presta (em vez de descartar sem dizer)
valid = pl.all_horizontal(*[~c.bad.fill_null(True) for c in CHECKS if c.severity == "error"])
good, bad = raw.filter(valid), raw.filter(~valid)
print(f"quarentena: {good.height:,} linhas boas + {bad.height:,} ruins = {good.height + bad.height:,} (conferem com {raw.height:,}? {good.height + bad.height == raw.height})")
bad.write_csv(work / "quarentena.csv")

# 4. as verificações que olham o CONJUNTO: volume, atualidade, integridade referencial, distribuição
daily_history = [480_000, 510_000, 495_000, 505_000, 490_000]          # volumes dos dias anteriores
mean, spread = sum(daily_history) / len(daily_history), max(daily_history) - min(daily_history)
for label, today in (("hoje normal", 497_000), ("hoje com a origem pela metade", 250_000)):
    anomaly = abs(today - mean) > spread * 2
    print(f"volume: {label}: {today:,} linhas (média {mean:,.0f}, tolerância ±{spread * 2:,.0f}) -> {'ANOMALIA' if anomaly else 'ok'}")

now = datetime(2026, 3, 2, 9, 0)
latest = good.select(pl.col("ts").str.to_datetime("%Y-%m-%dT%H:%M:%S").max()).item()
age = now - latest
print(f"atualidade: o evento mais recente é de {latest} ({age} atrás) -> {'DEFASADO (esperado < 6 h)' if age > timedelta(hours=6) else 'ok'}")

users = pl.DataFrame({"user_id": [str(i) for i in range(1, 49_000)]})
orphans = good.join(users, on="user_id", how="anti").height
print(f"integridade referencial: {orphans:,} eventos de usuários que não existem no cadastro ({orphans / good.height:.2%})")

# 5. o custo: as verificações são baratas perto do pipeline
start = time.perf_counter()
for _ in range(5):
    run_checks(raw, CHECKS)
print(f"\ncusto das verificações: {(time.perf_counter() - start) / 5 * 1e3:.0f} ms por rodada de {N:,} linhas ({N / ((time.perf_counter() - start) / 5):,.0f} linhas/s)")
