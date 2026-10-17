"""Exercício 6: janelas de tempo (tumbling) com marca d'água e tolerância a atraso, com memória limitada."""


class TumblingWindows:
    """Soma valores por (janela, chave) sobre um fluxo de eventos que chegam FORA DE ORDEM.

    * ``TumblingWindows(size, lateness)``: janelas de ``size`` segundos (``[0, size)``, ``[size, 2*size)``...); ``lateness`` é a
      tolerância de atraso, em segundos;
    * ``add(ts, key, value) -> list`` recebe UM evento (``ts`` é o tempo do evento, em segundos inteiros) e devolve a lista das
      janelas que FECHARAM por causa dele, cada uma como ``(inicio_da_janela, chave, total)``, ordenadas por início e depois por
      chave. A MARCA D'ÁGUA é ``max_ts_visto - lateness`` (``max_ts_visto`` considera o evento atual, mesmo que ele seja descartado
      depois): uma janela ``[w, w + size)`` fecha quando ``w + size <= marca`` (fecha SÓ quando a marca passar do fim, ou igualar);
    * um evento cuja janela JÁ fechou (``inicio + size <= marca`` antes de somá-lo, usando a marca calculada com o ``max_ts_visto``
      ANTERIOR ao evento) é DESCARTADO: não soma em nada e incrementa ``dropped``; senão soma ``value`` na janela dele (que pode estar
      aberta ou ser nova);
    * ``flush() -> list`` fecha e devolve TODAS as janelas abertas (mesmo formato e mesma ordem), esvaziando o estado;
    * ``open_windows`` é o número de janelas abertas agora (a memória do agregador); ``dropped`` o total de descartados;
    * ``size < 1`` ou ``lateness < 0``: ``ValueError``; ``ts`` negativo: ``ValueError``."""

    def __init__(self, size: int, lateness: int = 0):
        raise NotImplementedError

    def add(self, ts: int, key: str, value: float = 1.0) -> list:
        raise NotImplementedError

    def flush(self) -> list:
        raise NotImplementedError

    @property
    def open_windows(self) -> int:
        raise NotImplementedError

    @property
    def dropped(self) -> int:
        raise NotImplementedError


def batch_totals(events: list[tuple[int, str, float]], size: int) -> dict[tuple[int, str], float]:
    """A resposta certa em lote: ``{(inicio_da_janela, chave): soma}`` sobre TODOS os ``events`` (``(ts, chave, valor)``)."""
    raise NotImplementedError
