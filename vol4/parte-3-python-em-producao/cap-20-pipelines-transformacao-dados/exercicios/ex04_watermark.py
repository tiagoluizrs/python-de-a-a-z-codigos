"""Exercício 4: extração incremental com marca d'água, sobreposição (para dados atrasados) e idempotência."""
from datetime import datetime, timedelta


class IncrementalExtractor:
    """Busca apenas o que mudou desde a última execução.

    * ``IncrementalExtractor(state, fetch, overlap_minutes=0, key="id", cursor="updated_at")``: ``state`` é um dict que o CHAMADOR
      guarda (simula um arquivo); ``fetch(since: str) -> list[dict]`` devolve os registros com ``cursor`` ESTRITAMENTE maior que
      ``since`` (textos ISO ``"AAAA-MM-DDTHH:MM"``, comparáveis como texto);
    * ``run() -> dict`` faz uma rodada: lê a marca d'água de ``state["watermark"]`` (``"1970-01-01T00:00"`` se não houver), pede a
      ``fetch`` a partir de ``marca - overlap_minutes`` (para repegar registros que chegaram ATRASADOS), descarta os que a rodada JÁ
      entregou antes (compare por ``(key, cursor)`` em ``state["seen"]``, um conjunto de pares, para não devolver de novo o que já
      foi processado) e devolve ``{"new": [registros novos ou alterados, ordenados por (cursor, key)], "watermark": marca_nova,
      "fetched": quantos fetch devolveu}``;
    * a marca nova é o MAIOR ``cursor`` entre TODOS os registros que ``fetch`` devolveu (inclusive os já vistos); se ``fetch``
      devolver vazio ou só registros mais velhos que a marca atual, a marca NÃO anda para trás;
    * grave a marca e os pares vistos em ``state`` SÓ DEPOIS de montar o resultado (se ``fetch`` levantar exceção, ``state`` fica
      intacto e a exceção sobe);
    * para limitar a memória, ``state["seen"]`` guarda apenas os pares com ``cursor`` >= (marca nova - overlap_minutes): os mais
      antigos são esquecidos (já não podem voltar)."""

    def __init__(self, state: dict, fetch, overlap_minutes: int = 0, key: str = "id", cursor: str = "updated_at"):
        raise NotImplementedError

    def run(self) -> dict:
        raise NotImplementedError


def shift_minutes(iso: str, minutes: int) -> str:
    """Soma ``minutes`` (pode ser negativo) a um texto ``"AAAA-MM-DDTHH:MM"`` e devolve no mesmo formato."""
    raise NotImplementedError
