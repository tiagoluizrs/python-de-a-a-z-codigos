"""Duas peças instrumentadas ao mesmo tempo: métricas, rastros e logs de um fluxo "pedido -> estoque".

    python exemplos/shop_stack.py            roda, gera carga, imprime o que cada pilar mostra e sai
    python exemplos/shop_stack.py --serve    fica de pé em http://127.0.0.1:8000 (o /metrics é lido pelo Prometheus: compose.yaml)
"""
import io
import json
import random
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import httpx
import structlog
from opentelemetry import propagate, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from structlog.contextvars import bind_contextvars, clear_contextvars

# ---------- instrumentação ----------
REGISTRY = CollectorRegistry()
REQUESTS = Counter("shop_requests", "Requisições", ["service", "route", "status"], registry=REGISTRY)
LATENCY = Histogram("shop_request_seconds", "Duração", ["service", "route"], registry=REGISTRY,
                    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0))
IN_FLIGHT = Gauge("shop_in_flight", "Em andamento", ["service"], registry=REGISTRY)
SPANS = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(SPANS))
tracer = provider.get_tracer("shop")
LOG_STREAM = io.StringIO()
LOG_LOCK = threading.Lock()


class LockedStream:
    def write(self, text):
        with LOG_LOCK:
            return LOG_STREAM.write(text)

    def flush(self):
        pass


def add_trace_ids(logger, method, event):
    ctx = trace.get_current_span().get_span_context()
    if ctx.is_valid:
        event["trace_id"], event["span_id"] = format(ctx.trace_id, "032x"), format(ctx.span_id, "016x")
    return event


log = structlog.wrap_logger(structlog.PrintLogger(LockedStream()), processors=[
    structlog.contextvars.merge_contextvars, structlog.processors.add_log_level, add_trace_ids, structlog.processors.JSONRenderer()])

PRICES = {"SKU-1": 10.0, "SKU-2": 25.0, "SKU-3": 99.0}
STOCK = {"SKU-1": 100, "SKU-2": 3, "SKU-3": 0}


def instrumented(service: str, route: str, handler: BaseHTTPRequestHandler, work):
    """Mede, rastreia e loga uma requisição de qualquer serviço (um decorador manual, para ver tudo o que acontece)."""
    ctx = propagate.extract(dict(handler.headers))
    clear_contextvars()
    bind_contextvars(request_id=handler.headers.get("X-Request-Id", uuid.uuid4().hex[:8]), service=service)
    IN_FLIGHT.labels(service).inc()
    start = time.perf_counter()
    status = 200
    with tracer.start_as_current_span(f"{service} {route}", context=ctx, kind=SpanKind.SERVER) as span:
        try:
            body = work(span)
        except KeyError as error:
            status, body = 404, {"error": f"sem preço para {error}"}
            span.set_status(Status(StatusCode.ERROR, "produto desconhecido"))
            log.warning("produto_desconhecido", sku=str(error))
        except RuntimeError as error:
            status, body = 502, {"error": str(error)}
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            log.error("falha_dependencia", error=str(error))
        else:
            log.info("ok", route=route)
        span.set_attribute("http.status_code", status)
    elapsed = time.perf_counter() - start
    REQUESTS.labels(service, route, str(status)).inc()
    LATENCY.labels(service, route).observe(elapsed)
    IN_FLIGHT.labels(service).dec()
    payload = json.dumps(body).encode()
    handler.send_response(status)
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


class InventoryHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        sku = self.path.rsplit("/", 1)[-1]

        def work(span):
            span.set_attribute("sku", sku)
            time.sleep(random.uniform(0.002, 0.012) * (8 if random.random() < 0.04 else 1))        # 4% de lentidão
            if random.random() < 0.03:
                raise RuntimeError("banco do estoque indisponível")                                   # 3% de falha
            return {"sku": sku, "stock": STOCK[sku]}

        instrumented("inventory", "/stock", self, work)


class OrderHandler(BaseHTTPRequestHandler):
    inventory_url = ""
    client = None

    def log_message(self, *args):
        pass

    def do_GET(self):
        query = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}

        def work(span):
            sku, qty = query["sku"], int(query.get("qty", 1))
            span.set_attribute("order.sku", sku)
            price = PRICES[sku]
            with tracer.start_as_current_span("inventory.call", kind=SpanKind.CLIENT):
                headers = {"X-Request-Id": self.headers.get("X-Request-Id", "")}
                propagate.inject(headers)
                response = type(self).client.get(f"{type(self).inventory_url}/stock/{sku}", headers=headers)
            if response.status_code >= 500:
                raise RuntimeError(f"estoque respondeu {response.status_code}")
            return {"sku": sku, "total": price * qty, "available": response.json()["stock"] >= qty}

        instrumented("orders", "/order", self, work)


def start_servers(order_port=0):
    inventory = ThreadingHTTPServer(("127.0.0.1", 0), InventoryHandler)
    orders = ThreadingHTTPServer(("127.0.0.1", order_port), OrderHandler)
    for server in (inventory, orders):
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, daemon=True).start()
    OrderHandler.inventory_url = f"http://127.0.0.1:{inventory.server_port}"
    OrderHandler.client = httpx.Client(timeout=5)
    return inventory, orders


class MetricsHandler(OrderHandler):
    """O serviço de pedidos também serve /metrics (o que o Prometheus lê) e /healthz."""

    def do_GET(self):
        if self.path == "/metrics":
            payload = generate_latest(REGISTRY)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            super().do_GET()


def load(base: str, n: int, workers: int = 8):
    random.seed(7)
    skus = ["SKU-1", "SKU-1", "SKU-1", "SKU-2", "SKU-3", "SKU-9"]                 # SKU-9 não existe: gera 404

    def one(_):
        with httpx.Client(timeout=5) as client:
            return client.get(f"{base}/order", params={"sku": random.choice(skus), "qty": 1}, headers={"X-Request-Id": uuid.uuid4().hex[:8]}).status_code

    with ThreadPoolExecutor(workers) as pool:
        return list(pool.map(one, range(n)))


def quantile(q, buckets):
    total = buckets[-1][1]
    rank, prev_bound, prev_count = q * total, 0.0, 0
    for bound, count in buckets:
        if count >= rank:
            return prev_bound if bound == float("inf") else prev_bound + (bound - prev_bound) * (rank - prev_count) / max(count - prev_count, 1)
        prev_bound, prev_count = bound, count
    return prev_bound


if __name__ == "__main__":
    inventory, orders = start_servers(8000 if "--serve" in sys.argv else 0)
    orders.RequestHandlerClass = MetricsHandler
    base = f"http://127.0.0.1:{orders.server_port}"
    if "--serve" in sys.argv:
        print(f"no ar em {base}/order?sku=SKU-1 | métricas em {base}/metrics (Ctrl+C para sair)")
        threading.Thread(target=lambda: [load(base, 50) or time.sleep(1) for _ in iter(int, 1)], daemon=True).start()
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            sys.exit(130)

    start = time.perf_counter()
    statuses = load(base, 600)
    elapsed = time.perf_counter() - start
    print(f"600 requisições em {elapsed:.2f} s | status: { {s: statuses.count(s) for s in sorted(set(statuses))} }")

    # métricas: RED (taxa, erros, duração)
    get = REGISTRY.get_sample_value
    print("\nMÉTRICAS (o que mudou, agregado):")
    for service in ("orders", "inventory"):
        total = sum(v.value for m in REGISTRY.collect() if m.name == "shop_requests" for v in m.samples if v.name == "shop_requests_total" and v.labels["service"] == service)
        errors = sum(v.value for m in REGISTRY.collect() if m.name == "shop_requests" for v in m.samples
                     if v.name == "shop_requests_total" and v.labels["service"] == service and v.labels["status"].startswith("5"))
        route = "/order" if service == "orders" else "/stock"
        buckets = [(b, int(get("shop_request_seconds_bucket", {"service": service, "route": route, "le": str(b)}) or 0)) for b in
                   (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)]
        buckets.append((float("inf"), int(get("shop_request_seconds_count", {"service": service, "route": route}))))
        print(f"  {service:<10} {int(total):>4} req | erros 5xx {errors / total:6.1%} | p50 ~{quantile(0.5, buckets) * 1e3:5.1f} ms | p95 ~{quantile(0.95, buckets) * 1e3:6.1f} ms")

    # rastros: onde o tempo e o erro estão, para UMA requisição ruim
    spans = SPANS.get_finished_spans()
    failed = next((s for s in spans if s.name == "orders /order" and s.status.status_code == StatusCode.ERROR and s.attributes.get("http.status_code") == 502), None)
    print("\nRASTRO de uma requisição que falhou (502):")
    if failed:
        trace_id = failed.context.trace_id
        related = sorted((s for s in spans if s.context.trace_id == trace_id), key=lambda s: s.start_time)
        for s in related:
            depth = 0 if s.parent is None else (1 if s.name == "inventory.call" else 2)
            print(f"  {'  ' * depth}{s.name:<22} {(s.end_time - s.start_time) / 1e6:6.1f} ms  {s.status.status_code.name}"
                  + (f"  ({s.status.description})" if s.status.description else ""))
        print("\nLOGS da mesma requisição (achados pelo trace_id):")
        for line in LOG_STREAM.getvalue().splitlines():
            record = json.loads(line)
            if record.get("trace_id") == format(trace_id, "032x"):
                print("  ", {k: v for k, v in record.items() if k not in ("trace_id", "span_id")})
    print(f"\ntotal: {len(spans)} spans e {len(LOG_STREAM.getvalue().splitlines())} linhas de log para 600 requisições")
