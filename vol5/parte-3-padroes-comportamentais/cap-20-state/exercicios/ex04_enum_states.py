"""Exercício 4: estados como ``Enum`` com comportamento, e ``match`` para regras com lógica."""
from enum import Enum


class Light(Enum):
    """Um semáforo: ``RED`` (30 s), ``GREEN`` (25 s) e ``YELLOW`` (5 s). Cada membro tem a propriedade ``seconds`` (a duração) e o método ``next()`` que devolve o PRÓXIMO estado do
    ciclo ``RED -> GREEN -> YELLOW -> RED``. Implemente ``seconds`` e ``next`` SEM uma cadeia de ``if/elif`` (use dicionários no nível do módulo ou o ``value`` da enumeração)."""

    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"

    @property
    def seconds(self) -> int:
        raise NotImplementedError

    def next(self) -> "Light":
        raise NotImplementedError


class TrafficLight:
    """``TrafficLight(initial=Light.RED)``: um semáforo movido pelo TEMPO. ``state`` (``Light``) e ``elapsed`` (segundos já passados no estado atual, ``0 <= elapsed < seconds``).

    * ``tick(seconds)``: avança o relógio ``seconds`` segundos (``int`` ou ``float``) e troca de estado quantas vezes for preciso (um ``tick`` grande pode atravessar VÁRIOS estados);
      ``seconds < 0``: ``ValueError("tempo negativo")``; devolve a lista (possivelmente vazia) dos estados em que ENTROU, na ordem;
    * ``remaining``: quantos segundos faltam para trocar (``state.seconds - elapsed``);
    * ``TrafficLight.cycle_length()`` (método estático): a soma das durações de todos os estados (60)."""

    def __init__(self, initial: Light = Light.RED):
        raise NotImplementedError

    @property
    def state(self) -> Light:
        raise NotImplementedError

    @property
    def elapsed(self) -> float:
        raise NotImplementedError

    @property
    def remaining(self) -> float:
        raise NotImplementedError

    def tick(self, seconds: float) -> list[Light]:
        raise NotImplementedError

    @staticmethod
    def cycle_length() -> int:
        raise NotImplementedError


def door(state: str, event: str) -> str:
    """Uma porta com ``match``: estados ``"closed"``, ``"open"``, ``"locked"``; eventos ``"open"``, ``"close"``, ``"lock"``, ``"unlock"``. Devolve o NOVO estado.

    * ``closed``: ``open`` -> ``open``; ``lock`` -> ``locked``; ``close`` e ``unlock`` -> ``ValueError(f"{event} não permitido em {state}")``;
    * ``open``: ``close`` -> ``closed``; os demais eventos -> o mesmo ``ValueError``;
    * ``locked``: ``unlock`` -> ``closed``; os demais eventos -> o mesmo ``ValueError``;
    * estado desconhecido: ``ValueError(f"estado desconhecido: {state}")``; evento desconhecido (verificado DEPOIS do estado): ``ValueError(f"evento desconhecido: {event}")``.
    Use uma instrução ``match``."""
    raise NotImplementedError
