"""Logs que se ligam ao rastro e às métricas: structlog, trace_id, contexto por requisição, redação e custo."""
import io
import json
import logging
import time

import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from structlog.contextvars import bind_contextvars, clear_contextvars

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("shop")

SENSITIVE = {"password", "token", "authorization", "cpf", "card_number", "api_key"}


# 1. processadores: funções que enriquecem ou filtram cada evento antes de escrever
def add_trace_ids(logger, method, event_dict):
    """Liga o log ao rastro atual: o mesmo trace_id e span_id que o sistema de rastros mostra."""
    ctx = trace.get_current_span().get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def redact(logger, method, event_dict):
    for key in list(event_dict):
        if key.lower() in SENSITIVE:
            event_dict[key] = "***"
    return event_dict


def make_logger(stream):
    return structlog.wrap_logger(
        structlog.PrintLogger(stream),
        processors=[
            structlog.contextvars.merge_contextvars,              # request_id e companhia, vindos do contexto
            structlog.processors.add_log_level,
            add_trace_ids,
            redact,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
    )


stream = io.StringIO()
log = make_logger(stream)

# 2. uma requisição: o contexto é preso UMA vez e aparece em todos os logs dela, sem passar adiante
bind_contextvars(request_id="req-7f3a", route="/orders", user_tier="premium")
with tracer.start_as_current_span("POST /orders") as span:
    log.info("pedido_recebido", items=3, total=120.5)
    log.warning("estoque_baixo", sku="SKU-9", stock=2)
    log.info("login", user="ana", password="hunter2", authorization="Bearer abc.def")
    expected_trace = format(span.get_span_context().trace_id, "032x")
clear_contextvars()

print("logs em JSON (uma linha por evento, pesquisável por qualquer campo):")
records = [json.loads(line) for line in stream.getvalue().splitlines()]
for record in records:
    print("  ", {k: v for k, v in record.items() if k not in ("timestamp",)})
print("\nlog e rastro ligados? (o trace_id do log é o do span):", all(r["trace_id"] == expected_trace for r in records))
print("segredos mascarados:", records[2]["password"], records[2]["authorization"], "| campos do contexto em todos:", all("request_id" in r for r in records))

# 3. o que NÃO fazer: formatar no ato (f-string) e logar o que nunca será lido
std = logging.getLogger("cost")
std.setLevel(logging.INFO)
std.addHandler(logging.NullHandler())
std.propagate = False
N = 200_000
big = {"k": list(range(50))}

start = time.perf_counter()
for _ in range(N):
    std.debug(f"payload {big}")                        # f-string avalia SEMPRE, mesmo com o nível desligado
t_fstring = (time.perf_counter() - start) / N * 1e9
start = time.perf_counter()
for _ in range(N):
    std.debug("payload %s", big)                       # formatação preguiçosa: só se for emitido
t_lazy = (time.perf_counter() - start) / N * 1e9
start = time.perf_counter()
for _ in range(N):
    if std.isEnabledFor(logging.DEBUG):
        std.debug("payload %s", compute := str(big))
t_guard = (time.perf_counter() - start) / N * 1e9
print(f"\nlog DEBUG desligado: f-string {t_fstring:7.0f} ns | %s preguiçoso {t_lazy:5.0f} ns | com isEnabledFor {t_guard:5.0f} ns")

# 4. o custo de emitir: texto, JSON e structlog completo
sink = io.StringIO()
text_logger = logging.getLogger("text")
text_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sink)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
text_logger.addHandler(handler)
text_logger.propagate = False
M = 20_000
start = time.perf_counter()
for i in range(M):
    text_logger.info("pedido %d recebido, total %.2f", i, 120.5)
t_text = (time.perf_counter() - start) / M * 1e6
sink2 = io.StringIO()
slog = make_logger(sink2)
start = time.perf_counter()
for i in range(M):
    slog.info("pedido_recebido", order=i, total=120.5)
t_struct = (time.perf_counter() - start) / M * 1e6
with tracer.start_as_current_span("x"):
    start = time.perf_counter()
    for i in range(M):
        slog.info("pedido_recebido", order=i, total=120.5)
    t_struct_span = (time.perf_counter() - start) / M * 1e6
print(f"\nlog emitido: logging em texto {t_text:6.1f} µs | structlog em JSON {t_struct:6.1f} µs | structlog em JSON dentro de um span {t_struct_span:6.1f} µs")

# 5. amostrar logs de alto volume: um evento por request de 10.000 req/s é caro e quase nunca é lido
import random

random.seed(1)
kept = sum(1 for _ in range(100_000) if random.random() < 0.01)
print(f"\namostragem de logs INFO de alto volume a 1%: {kept} de 100.000 guardados (erros e avisos: sempre 100%)")

# 6. um id por requisição: a primeira pergunta de quem investiga
print("\nregra: o que o usuário reclama -> request_id -> todos os logs -> trace_id -> o rastro -> a métrica que dispara o alerta")
