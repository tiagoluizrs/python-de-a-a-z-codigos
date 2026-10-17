"""Rastros distribuídos com OpenTelemetry: spans, atributos, erros, propagação entre serviços, amostragem e custo."""
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
from opentelemetry import context, propagate, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from opentelemetry.trace import SpanKind, Status, StatusCode

exporter = InMemorySpanExporter()
provider = TracerProvider(resource=Resource.create({"service.name": "demo"}))
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("shop")


# 1. spans: o que aconteceu, quanto durou, dentro de quem
def checkout():
    with tracer.start_as_current_span("checkout") as span:
        span.set_attribute("order.items", 3)                      # atributo: dado de ALTA cardinalidade vai aqui, não em métrica
        with tracer.start_as_current_span("validate"):
            time.sleep(0.003)
        with tracer.start_as_current_span("charge") as charge:
            charge.set_attribute("payment.method", "card")
            charge.add_event("gateway_called", {"attempt": 1})     # evento: um ponto no tempo dentro do span
            time.sleep(0.01)
        return span


checkout()
spans = exporter.get_finished_spans()
by_id = {s.context.span_id: s for s in spans}


def tree(span, depth=0):
    ms = (span.end_time - span.start_time) / 1e6
    print(f"  {'  ' * depth}{span.name:<10} {ms:6.1f} ms  trace={format(span.context.trace_id, '032x')[:8]}… attrs={dict(span.attributes)}")
    for child in sorted((s for s in spans if s.parent and s.parent.span_id == span.context.span_id), key=lambda s: s.start_time):
        tree(child, depth + 1)


print("árvore do rastro (um trace_id para tudo):")
for root in (s for s in spans if s.parent is None):
    tree(root)
print("evento no span 'charge':", [(e.name, dict(e.attributes)) for s in spans if s.name == "charge" for e in s.events])

# 2. erros: record_exception e o status do span
exporter.clear()
try:
    with tracer.start_as_current_span("charge") as span:
        raise TimeoutError("gateway não respondeu")
except TimeoutError:
    pass
failed = exporter.get_finished_spans()[0]
print("\nspan com erro:", failed.status.status_code.name, "|", failed.status.description, "| evento:", failed.events[0].name, dict(failed.events[0].attributes)["exception.type"])

# 3. propagação: dois serviços, um rastro só (o cabeçalho W3C `traceparent` carrega o contexto)
class Inventory(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        ctx = propagate.extract(dict(self.headers))               # lê o `traceparent` que chegou
        with tracer.start_as_current_span("inventory.lookup", context=ctx, kind=SpanKind.SERVER) as span:
            span.set_attribute("sku", self.path.rsplit("/", 1)[-1])
            time.sleep(0.01)
            body = b'{"stock": 7}'
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), Inventory)
server.daemon_threads = True
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_port}"

httpx.get(BASE + "/warmup")                                       # a primeira conexão custa mais: não entra na conta
exporter.clear()
with tracer.start_as_current_span("order.create", kind=SpanKind.SERVER):
    headers: dict[str, str] = {}
    propagate.inject(headers)                                      # escreve o `traceparent` nos cabeçalhos da chamada
    print("\ncabeçalho enviado:", headers)
    with tracer.start_as_current_span("inventory.call", kind=SpanKind.CLIENT):
        propagate.inject(headers)
        httpx.get(BASE + "/stock/SKU-9", headers=headers)
spans = exporter.get_finished_spans()
by_name = {s.name: s for s in spans}
print("mesmo trace_id nos três spans?", len({s.context.trace_id for s in spans}) == 1,
      "| o serviço de estoque é filho de 'inventory.call'?", by_name["inventory.lookup"].parent.span_id == by_name["inventory.call"].context.span_id)
for root in (s for s in spans if s.parent is None):
    tree(root)

# 4. amostragem: guardar TODOS os rastros custa; guardar uma fração (consistente entre serviços) basta
class Counting(SpanExporter):
    def __init__(self):
        self.count = 0

    def export(self, spans):
        self.count += len(spans)
        return SpanExportResult.SUCCESS


for ratio in (1.0, 0.1, 0.01):
    counting = Counting()
    sampled = TracerProvider(sampler=ParentBased(TraceIdRatioBased(ratio)))
    sampled.add_span_processor(SimpleSpanProcessor(counting))
    sampled_tracer = sampled.get_tracer("s")
    for _ in range(10_000):
        with sampled_tracer.start_as_current_span("request"):
            pass
    print(f"amostragem {ratio:>5.0%}: {counting.count:>6,} de 10.000 rastros guardados")


# 5. o custo de instrumentar (por span), com e sem exportar
class Slow(Counting):
    """Um exportador que demora (como uma chamada de rede para um coletor): 1 ms por lote."""

    def export(self, spans):
        time.sleep(0.001)
        return super().export(spans)


def cost(provider_, n=20_000):
    t = provider_.get_tracer("c")
    start = time.perf_counter()
    for _ in range(n):
        with t.start_as_current_span("op") as s:
            s.set_attribute("k", "v")
    return (time.perf_counter() - start) / n * 1e6


noop = trace.NoOpTracer()
start = time.perf_counter()
for _ in range(20_000):
    with noop.start_as_current_span("op"):
        pass
t_noop = (time.perf_counter() - start) / 20_000 * 1e6
dropped = TracerProvider(sampler=TraceIdRatioBased(0.0))
fast_batch = TracerProvider()
fast_batch.add_span_processor(BatchSpanProcessor(Counting(), max_queue_size=50_000, schedule_delay_millis=200))
slow_batch = TracerProvider()
slow_batch.add_span_processor(BatchSpanProcessor(Slow(), max_queue_size=50_000, schedule_delay_millis=200))
slow_simple = TracerProvider()
slow_simple.add_span_processor(SimpleSpanProcessor(Slow()))
print(f"\ncusto por span: sem SDK (no-op) {t_noop:5.2f} µs | SDK, não amostrado {cost(dropped):5.2f} µs | amostrado, exportador rápido (Batch) {cost(fast_batch):6.2f} µs")
print(f"com um exportador LENTO (1 ms por envio, como uma rede): BatchSpanProcessor {cost(slow_batch, 2_000):8.2f} µs por span | SimpleSpanProcessor {cost(slow_simple, 2_000):9.2f} µs por span")
fast_batch.shutdown()
slow_batch.shutdown()
print("(a decisão de NÃO amostrar é barata; o SimpleSpanProcessor exporta DENTRO da requisição: em produção, sempre Batch)")

# 6. o contexto atual é um contextvar: spans filhos em threads precisam do contexto passado à mão
results = []
with tracer.start_as_current_span("parent") as parent:
    token = context.attach(trace.set_span_in_context(parent))
    try:
        def worker():
            results.append(trace.get_current_span().get_span_context().trace_id == parent.get_span_context().trace_id)
        t = threading.Thread(target=worker)
        t.start()
        t.join()
        ctx = context.get_current()
        t2 = threading.Thread(target=lambda: (context.attach(ctx), results.append(trace.get_current_span().get_span_context().trace_id == parent.get_span_context().trace_id)))
        t2.start()
        t2.join()
    finally:
        context.detach(token)
print("\ncontexto em uma thread nova: sem passar ->", results[0], "| passando o contexto ->", results[1])
server.shutdown()
