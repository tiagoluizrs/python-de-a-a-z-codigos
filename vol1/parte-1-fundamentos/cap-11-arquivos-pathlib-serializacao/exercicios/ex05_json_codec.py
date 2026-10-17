"""Exercício 5: JSON para dataclasses com Decimal, datetime e date."""
import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Order:
    id: int
    customer: str
    total: Decimal
    created: datetime
    due: date


def dumps(obj) -> str:
    """Serialize ``obj`` (dataclass, dict, lista...) para JSON.

    Regras de formato (use ``json.dumps(..., default=...)``):
    - dataclass vira objeto JSON com os nomes dos campos;
    - ``Decimal`` vira TEXTO (``"19.90"``), nunca número, para não
      perder precisão;
    - ``datetime`` e ``date`` viram texto ISO 8601 (``isoformat()``);
    - qualquer outro tipo sem regra levanta ``TypeError``.
    A saída deve ser determinística (``sort_keys=True``).
    """
    raise NotImplementedError


def loads_as(cls, text: str):
    """Leia ``text`` (um objeto JSON) e devolva uma instância de ``cls``.

    ``cls`` é uma dataclass. Use ``typing.get_type_hints(cls)`` para
    descobrir o tipo de cada campo e converta o valor lido:
    ``Decimal(texto)``, ``datetime.fromisoformat``,
    ``date.fromisoformat``; ``int`` e ``str`` já vêm prontos.
    Campo obrigatório ausente deve levantar ``KeyError``.
    """
    raise NotImplementedError
