"""Transformar métricas em decisões: SLI, SLO, orçamento de erro, queima e verificações de saúde."""
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

# 1. SLI (o que se mede) e SLO (a meta): disponibilidade = requisições boas / total
SLO = 0.999                                      # 99,9% em 30 dias
WINDOW_DAYS = 30
total_30d = 43_200_000                           # 1 milhão e 440 mil por dia
bad_30d = 31_000
sli = 1 - bad_30d / total_30d
budget = (1 - SLO) * total_30d                   # o orçamento de erro: quantas requisições RUINS a meta tolera
print(f"SLI medido: {sli:.4%} | meta (SLO): {SLO:.1%} | orçamento de erro: {budget:,.0f} requisições ruins | gastas: {bad_30d:,} ({bad_30d / budget:.0%})")
minutes = WINDOW_DAYS * 24 * 60
print(f"99,9% em {WINDOW_DAYS} dias = {minutes * (1 - SLO):.1f} minutos de indisponibilidade tolerados | 99,99%: {minutes * 1e-4:.1f} min | 99%: {minutes * 0.01 / 60:.1f} horas")


# 2. taxa de queima (burn rate): com que velocidade o orçamento está sendo gasto
def burn_rate(bad: int, total: int, slo: float = SLO) -> float:
    """1,0 = gastando exatamente no ritmo que esgota o orçamento no fim da janela; 14,4 = esgota em 2 dias."""
    return (bad / total) / (1 - slo) if total else 0.0


print("\nqueima por janela (erros / requisições):")
for label, bad, total in [("5 min, normal", 12, 12_000), ("5 min, incidente", 1_800, 12_000), ("1 h", 900, 720_000), ("1 h", 12_000, 720_000)]:
    rate = burn_rate(bad, total)
    days = WINDOW_DAYS / rate if rate else float("inf")
    print(f"  {label:<18} {bad:>6,} de {total:>7,} -> taxa {rate:6.1f}x | no ritmo, esgota o orçamento em {days:6.1f} dias")


def should_page(short_burn: float, long_burn: float, threshold: float = 14.4) -> bool:
    """Alerta com DUAS janelas (curta e longa): a longa evita falso positivo de um pico; a curta apaga o alerta quando acaba."""
    return short_burn >= threshold and long_burn >= threshold


print("\nalerta de duas janelas (5 min e 1 h, limiar 14,4x):")
print("  pico de 5 min, hora normal ->", should_page(burn_rate(1_800, 12_000), burn_rate(900, 720_000)))
print("  incidente sustentado       ->", should_page(burn_rate(1_800, 12_000), burn_rate(12_000, 720_000)))

# 3. a regra de alerta no Prometheus (o mesmo cálculo, em YAML; não executamos aqui)
RULE = """\
groups:
- name: shop-slo
  rules:
  - alert: ErrorBudgetBurnFast
    expr: |
      (sum(rate(shop_requests_total{status=~"5.."}[5m])) / sum(rate(shop_requests_total[5m]))) > (14.4 * 0.001)
      and
      (sum(rate(shop_requests_total{status=~"5.."}[1h])) / sum(rate(shop_requests_total[1h]))) > (14.4 * 0.001)
    for: 2m
    labels: {severity: page}
    annotations: {summary: "Orçamento de erro esgotando em ~2 dias"}
"""
print("\nregra de alerta (Prometheus):\n" + "".join("  " + line + "\n" for line in RULE.splitlines()[:9]) + "  ...")


# 4. saúde: liveness (estou vivo?), readiness (posso receber tráfego?) e as dependências, com limite de tempo
class Deps:
    db_ok = True
    cache_slow = False


def check_db():
    if not Deps.db_ok:
        raise ConnectionError("banco indisponível")


def check_cache():
    time.sleep(2.0 if Deps.cache_slow else 0.001)


def run_checks(checks: dict, timeout: float = 0.5):
    results = {}
    pool = ThreadPoolExecutor(len(checks))             # SEM `with`: o `with` esperaria a thread lenta terminar ao sair, anulando o timeout
    futures = {name: pool.submit(fn) for name, fn in checks.items()}
    start = time.perf_counter()
    for name, future in futures.items():
        try:
            future.result(timeout=max(timeout - (time.perf_counter() - start), 0.001))
            results[name] = "ok"
        except TimeoutError:
            results[name] = f"timeout > {timeout}s"
        except Exception as error:
            results[name] = f"falhou: {error}"
    pool.shutdown(wait=False, cancel_futures=True)
    return results


class Health(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/livez":                           # só diz que o PROCESSO responde; NUNCA checa dependências
            status, body = 200, {"status": "alive"}
        elif self.path == "/readyz":                        # pronto para tráfego? depende das dependências críticas
            checks = run_checks({"db": check_db, "cache": check_cache})
            critical_ok = checks["db"] == "ok"               # o cache lento degrada, mas não derruba
            status, body = (200 if critical_ok else 503), {"status": "ready" if critical_ok else "not ready", "checks": checks}
        else:
            status, body = 404, {}
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


server = ThreadingHTTPServer(("127.0.0.1", 0), Health)
server.daemon_threads = True
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_port}"

print("\nsaúde:")
for label, db_ok, cache_slow in [("tudo bem", True, False), ("banco caiu", False, False), ("cache lento", True, True)]:
    Deps.db_ok, Deps.cache_slow = db_ok, cache_slow
    start = time.perf_counter()
    live = httpx.get(BASE + "/livez")
    ready = httpx.get(BASE + "/readyz")
    print(f"  {label:<12} /livez {live.status_code} | /readyz {ready.status_code} {ready.json()['checks']} em {(time.perf_counter() - start) * 1e3:.0f} ms")
print("(liveness que consulta o banco reinicia TODOS os pods quando o banco cai; readiness só tira do balanceador)")
server.shutdown()
