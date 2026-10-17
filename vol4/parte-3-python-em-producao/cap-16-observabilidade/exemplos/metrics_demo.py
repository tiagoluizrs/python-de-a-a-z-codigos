"""Métricas com prometheus_client: contadores, medidores, histogramas, rótulos e o custo de cada um."""
import time
import tracemalloc

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary, generate_latest

registry = CollectorRegistry()           # um registro PRÓPRIO: testável e sem o que outras bibliotecas registraram

REQUESTS = Counter("shop_requests", "Requisições atendidas", ["route", "status"], registry=registry)
IN_FLIGHT = Gauge("shop_in_flight", "Requisições em andamento", registry=registry)
LATENCY = Histogram("shop_request_seconds", "Duração das requisições", ["route"], registry=registry,
                    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0))
PAYLOAD = Summary("shop_payload_bytes", "Tamanho dos corpos", registry=registry)

# 1. as quatro formas de métrica
for status in ("200", "200", "200", "500"):
    REQUESTS.labels(route="/orders", status=status).inc()
IN_FLIGHT.inc()
IN_FLIGHT.inc()
IN_FLIGHT.dec()
for seconds in (0.004, 0.012, 0.03, 0.03, 0.2, 0.7):
    LATENCY.labels(route="/orders").observe(seconds)
PAYLOAD.observe(512)

print("formato de exposição (o que o /metrics devolve e o Prometheus lê):")
text = generate_latest(registry).decode()
wanted = ("# TYPE shop_requests_total", "shop_requests_total{", "shop_in_flight ", "# TYPE shop_request_seconds ",
          'shop_request_seconds_bucket{le="0.025"', 'shop_request_seconds_bucket{le="0.25"', 'shop_request_seconds_bucket{le="+Inf"',
          "shop_request_seconds_count", "shop_request_seconds_sum")
for line in text.splitlines():
    if line.startswith(wanted):
        print("  ", line)

# 2. o histograma guarda CONTAGENS por faixa (cumulativas); o percentil é ESTIMADO por interpolação
def quantile(q: float, buckets: list[tuple[float, int]]) -> float:
    """histogram_quantile do Prometheus: interpola linearmente dentro da faixa que contém o percentil."""
    total = buckets[-1][1]
    rank = q * total
    previous_bound, previous_count = 0.0, 0
    for bound, count in buckets:
        if count >= rank:
            if bound == float("inf"):
                return previous_bound
            return previous_bound + (bound - previous_bound) * (rank - previous_count) / max(count - previous_count, 1)
        previous_bound, previous_count = bound, count
    return previous_bound


samples = registry.get_sample_value
buckets = [(float(b), int(samples("shop_request_seconds_bucket", {"route": "/orders", "le": str(b)}))) for b in (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)]
buckets.append((float("inf"), int(samples("shop_request_seconds_count", {"route": "/orders"}))))
print(f"\nbuckets cumulativos: {[c for _, c in buckets]} | p50 ~ {quantile(0.5, buckets) * 1e3:.0f} ms | p95 ~ {quantile(0.95, buckets) * 1e3:.0f} ms")
print("os valores reais eram [4, 12, 30, 30, 200, 700] ms: a estimativa é boa só se os buckets cobrem a região que importa")

# 3. o custo de registrar uma métrica (no caminho quente da aplicação)
N = 200_000
counter = REQUESTS.labels(route="/hot", status="200")
start = time.perf_counter()
for _ in range(N):
    counter.inc()
t_inc = (time.perf_counter() - start) / N * 1e9
start = time.perf_counter()
for _ in range(N):
    REQUESTS.labels(route="/hot", status="200").inc()
t_labels = (time.perf_counter() - start) / N * 1e9
hist = LATENCY.labels(route="/hot")
start = time.perf_counter()
for _ in range(N):
    hist.observe(0.03)
t_obs = (time.perf_counter() - start) / N * 1e9
print(f"\ncusto: counter.inc() {t_inc:6.0f} ns | .labels(...).inc() {t_labels:6.0f} ns | histogram.observe() {t_obs:6.0f} ns")
print("(guarde o filho `.labels(...)` em uma variável quando o caminho é quente: poupa a busca pelo rótulo)")

# 4. a explosão de cardinalidade: cada combinação de rótulos é uma SÉRIE na memória (e no Prometheus)
bad = CollectorRegistry()
by_user = Counter("by_user", "ruim: um rótulo por usuário", ["user_id"], registry=bad)
good = CollectorRegistry()
by_route = Counter("by_route", "bom: rótulo de poucos valores", ["route"], registry=good)
tracemalloc.start()
start = time.perf_counter()
for user_id in range(50_000):
    by_user.labels(user_id=str(user_id)).inc()
t_bad = (time.perf_counter() - start) * 1e3
mem_bad = tracemalloc.get_traced_memory()[0] / 1e6
tracemalloc.stop()
tracemalloc.start()
start = time.perf_counter()
for user_id in range(50_000):
    by_route.labels(route=("/orders", "/items", "/health")[user_id % 3]).inc()
t_good = (time.perf_counter() - start) * 1e3
mem_good = tracemalloc.get_traced_memory()[0] / 1e6
tracemalloc.stop()
series_bad = len(generate_latest(bad).decode().splitlines())
series_good = len(generate_latest(good).decode().splitlines())
print(f"\ncardinalidade: rótulo por usuário -> 50.000 séries, {mem_bad:5.1f} MB, {t_bad:6.0f} ms, {series_bad:,} linhas na exposição")
print(f"               rótulo por rota    ->      3 séries, {mem_good:5.2f} MB, {t_good:6.0f} ms, {series_good} linhas na exposição")
print("(o ID de usuário/pedido/URL completa NUNCA vai em um rótulo: vai em log ou em atributo de trace)")

# 5. medir o TEMPO de um bloco: o contexto do Histogram
with LATENCY.labels(route="/timed").time():
    time.sleep(0.02)
print("\nwith histogram.time():", round(samples("shop_request_seconds_sum", {"route": "/timed"}) * 1e3), "ms registrados")
