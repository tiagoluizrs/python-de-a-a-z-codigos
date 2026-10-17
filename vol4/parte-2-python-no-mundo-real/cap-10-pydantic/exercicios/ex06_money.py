"""Exercício 6: um tipo Money reutilizável e uma fatura."""
from pydantic import BaseModel  # noqa: F401

# Money: ``Annotated[Decimal, ...]`` que
#   * aceita ``Decimal``, ``int`` e ``str`` numérica (com vírgula decimal ``"9,90"`` também), e ``float`` COM aviso de arredondamento:
#     aceite ``float`` convertendo por ``str`` (``0.1 + 0.2`` vira ``Decimal("0.30")``), mas RECUSE ``bool`` e ``NaN``/infinito;
#   * arredonda para 2 casas com ``ROUND_HALF_EVEN`` (use um ``BeforeValidator`` ou ``AfterValidator``);
#   * serializa para JSON como ``str`` com 2 casas (``"29.70"``) (use ``PlainSerializer(..., when_used="json")``);
#   * não pode ser negativo (``ge=0``).
Money = None   # substitua pela sua definição


class Item(BaseModel):
    """``name`` (texto), ``price`` (``Money``), ``qty`` (inteiro >= 1)."""


class Invoice(BaseModel):
    """``items``: lista de ``Item`` com pelo menos 1; ``discount``: ``Money`` (padrão ``0``); campo calculado ``total`` = soma de
    ``price * qty`` menos ``discount``, arredondado a 2 casas (``Money``); o desconto não pode ser MAIOR que o subtotal
    (``ValueError`` em um ``model_validator``: ``"desconto maior que o total"``)."""
