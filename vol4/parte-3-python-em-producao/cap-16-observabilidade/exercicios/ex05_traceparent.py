"""Exercício 5: o cabeçalho ``traceparent`` do W3C (o que liga os rastros de serviços diferentes)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TraceContext:
    trace_id: str        # 32 caracteres hexadecimais minúsculos
    span_id: str         # 16 caracteres hexadecimais minúsculos
    sampled: bool


def parse_traceparent(header: str) -> TraceContext:
    """Lê ``00-<trace_id>-<span_id>-<flags>`` (ex.: ``00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01``).

    * exatamente 4 campos separados por ``-``; versão ``00`` (outra: ``ValueError``);
    * ``trace_id``: 32 hex minúsculos, não pode ser só zeros; ``span_id``: 16 hex minúsculos, não pode ser só zeros;
    * ``flags``: 2 hex; ``sampled`` é o bit menos significativo (``01`` -> ``True``, ``00`` -> ``False``, ``03`` -> ``True``);
    * espaços nas pontas do cabeçalho inteiro são ignorados; qualquer violação: ``ValueError`` com uma mensagem útil
      (qual campo falhou)."""
    raise NotImplementedError


def format_traceparent(ctx: TraceContext) -> str:
    """O caminho inverso: ``00-<trace_id>-<span_id>-01`` (se ``sampled``) ou ``-00`` (se não)."""
    raise NotImplementedError


def child_of(ctx: TraceContext, rng) -> TraceContext:
    """Um contexto FILHO: mesmo ``trace_id`` e ``sampled``, ``span_id`` novo com 16 hex minúsculos gerado a partir de
    ``rng`` (um ``random.Random``: ``rng.getrandbits(64)``). Nunca devolva um ``span_id`` só de zeros (sorteie de novo)."""
    raise NotImplementedError


def should_sample(trace_id: str, ratio: float) -> bool:
    """Decisão de amostragem DETERMINÍSTICA a partir do ``trace_id``, para todos os serviços decidirem igual sem se falar:
    use os 16 últimos caracteres hex como um inteiro ``n`` e devolva ``n / 2**64 < ratio``. ``ratio`` fora de ``[0, 1]``:
    ``ValueError``. ``ratio == 1`` sempre ``True``; ``0`` sempre ``False``."""
    raise NotImplementedError
