"""Gabarito do exercício 5."""
import re
from dataclasses import dataclass

_HEX = re.compile(r"^[0-9a-f]+$")


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    span_id: str
    sampled: bool


def _hex(name, text, size):
    if len(text) != size or not _HEX.match(text):
        raise ValueError(f"{name} deve ter {size} caracteres hexadecimais minúsculos: {text!r}")
    if set(text) == {"0"}:
        raise ValueError(f"{name} não pode ser só zeros")
    return text


def parse_traceparent(header):
    parts = header.strip().split("-")
    if len(parts) != 4:
        raise ValueError(f"traceparent deve ter 4 campos, tem {len(parts)}")
    version, trace_id, span_id, flags = parts
    if version != "00":
        raise ValueError(f"versão não suportada: {version!r}")
    _hex("trace_id", trace_id, 32)
    _hex("span_id", span_id, 16)
    if len(flags) != 2 or not _HEX.match(flags):
        raise ValueError(f"flags deve ter 2 hexadecimais: {flags!r}")
    return TraceContext(trace_id, span_id, bool(int(flags, 16) & 1))


def format_traceparent(ctx):
    return f"00-{ctx.trace_id}-{ctx.span_id}-{'01' if ctx.sampled else '00'}"


def child_of(ctx, rng):
    span_id = 0
    while span_id == 0:
        span_id = rng.getrandbits(64)
    return TraceContext(ctx.trace_id, f"{span_id:016x}", ctx.sampled)


def should_sample(trace_id, ratio):
    if not 0 <= ratio <= 1:
        raise ValueError("ratio deve estar em [0, 1]")
    if ratio >= 1:
        return True
    return int(trace_id[-16:], 16) / 2**64 < ratio
