"""Séries temporais: índice de datas, resample, janelas móveis, fusos e feriados."""
import numpy as np
import pandas as pd

from sample_data import make_orders

orders = make_orders(100_000)

# 1. um índice de datas dá fatias por texto e agregação por período
ts = orders.set_index("date").sort_index()
print("índice:", ts.index.dtype, "| primeiro:", ts.index[0], "| último:", ts.index[-1])
print("fatia por texto 2025-03:", len(ts.loc["2025-03"]), "linhas | 2025-03-10 a 2025-03-12:", len(ts.loc["2025-03-10":"2025-03-12"]))

# 2. resample: o groupby por janela de tempo
daily = ts["total"].resample("D").sum()
weekly = ts["total"].resample("W").agg(["sum", "count"])
monthly = ts["total"].resample("MS").sum()
print("\nvendas por dia:", len(daily), "dias | por semana:", len(weekly), "| por mês (início):", monthly.index[:3].strftime("%Y-%m").tolist())
print("meses:\n", monthly.round(0).head(3).to_string())

# 3. janelas móveis, defasagem e variação
daily7 = daily.rolling(7).mean()
print("\nmédia móvel de 7 dias (os 6 primeiros são NaN):", daily7.iloc[:8].round(0).tolist())
print("rolling(7, min_periods=1) preenche o começo:", daily.rolling(7, min_periods=1).mean().iloc[:2].round(0).tolist())
change = daily.pct_change()
print("pct_change dia a dia (primeiros):", change.iloc[1:4].round(3).tolist(), "| shift(1):", daily.shift(1).iloc[1] == daily.iloc[0])
growth = daily.diff()
print("diff:", growth.iloc[1:4].round(0).tolist(), "| acumulado (cumsum) no fim do ano:", f"{daily.cumsum().iloc[-1]:,.0f}")
print("janela por tempo (7D), não por linhas:", ts["total"].rolling("7D").sum().iloc[-1].round(0))

# 4. buracos na série: asfreq e reindex mostram, fillna/ffill/interpolate resolvem
sparse = daily[daily.index.dayofweek < 5]                             # sem fins de semana
full = sparse.asfreq("D")
print(f"\nsem fins de semana: {len(sparse)} dias | asfreq('D') reabre os buracos: {len(full)} dias, {int(full.isna().sum())} NaN")
gap = full.index[full.isna()][0]
print(f"no primeiro buraco ({gap.date()}, {gap.day_name()}): ffill {full.ffill()[gap]:,.0f} | interpolate {full.interpolate()[gap]:,.0f} | fillna(0) {full.fillna(0)[gap]:,.0f}")

# 5. componentes da data com .dt (vetorizado)
dates = orders["date"]
by_hour = dates.dt.hour.value_counts().sort_index()
weekday = orders.groupby(dates.dt.day_name())["total"].sum().round(0)
print("\nhoras do dia com mais pedidos:", by_hour.nlargest(3).index.tolist(), "| dia da semana:", weekday.sort_values().index[-1])
print("trimestre:", dates.dt.quarter.unique().tolist(), "| é fim de mês?", int(dates.dt.is_month_end.sum()), "pedidos")

# 6. fuso horário: guarde em UTC, converta só para mostrar
utc = pd.Series(pd.to_datetime(["2026-03-08 06:30", "2026-03-08 07:30"])).dt.tz_localize("UTC")
sp = utc.dt.tz_convert("America/Sao_Paulo")
ny = utc.dt.tz_convert("America/New_York")
print("\nUTC       :", utc.dt.strftime("%Y-%m-%d %H:%M %Z").tolist())
print("São Paulo :", sp.dt.strftime("%Y-%m-%d %H:%M %Z").tolist(), "(sem horário de verão desde 2019)")
print("Nova York :", ny.dt.strftime("%Y-%m-%d %H:%M %Z").tolist(), "(o horário de verão começa às 2h locais de 8/3: 07:00 UTC; EST vira EDT)")

# 7. datas "em texto" pedem formato explícito (o Capítulo 12 do Volume 1 mostrou o custo do dia/mês ambíguo)
raw = pd.Series(["01/02/2026", "13/02/2026"])
print("\nformat explícito:", pd.to_datetime(raw, format="%d/%m/%Y").dt.strftime("%Y-%m-%d").tolist())
print("dayfirst sem format (adivinha, avisa se não bater):", pd.to_datetime(raw, dayfirst=True).dt.strftime("%Y-%m-%d").tolist())
print("errors='coerce' vira NaT (o 'NaN' das datas):", pd.to_datetime(pd.Series(["2026-01-01", "quando der"]), errors="coerce").tolist())

# 8. períodos e dias úteis
period = pd.period_range("2026-01", periods=3, freq="M")
print("\nPeriodIndex:", period.astype(str).tolist(), "| dias úteis de março de 2026:", len(pd.bdate_range("2026-03-01", "2026-03-31")))
print("Timedelta:", (pd.Timestamp("2026-03-10") - pd.Timestamp("2026-03-01")).days, "dias | adicionar 1 mês:", (pd.Timestamp("2026-01-31") + pd.DateOffset(months=1)).date())
