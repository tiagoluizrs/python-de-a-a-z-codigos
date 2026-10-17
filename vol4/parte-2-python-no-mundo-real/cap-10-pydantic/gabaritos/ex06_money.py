"""Gabarito do exercício 6."""
import math
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, PlainSerializer, computed_field, model_validator

TWO = Decimal("0.01")


def _to_decimal(value):
    if isinstance(value, bool):
        raise ValueError("bool não é valor monetário")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("valor não finito")
        return Decimal(str(round(value, 10)))
    if isinstance(value, str):
        try:
            return Decimal(value.strip().replace(",", "."))
        except InvalidOperation as error:                # InvalidOperation NÃO é ValueError: o Pydantic não a converte em erro de validação
            raise ValueError("valor monetário inválido") from error
    return value


def _quantize(value):
    return value.quantize(TWO, rounding=ROUND_HALF_EVEN)


Money = Annotated[
    Decimal,
    BeforeValidator(_to_decimal),
    Field(ge=0),
    AfterValidator(_quantize),
    PlainSerializer(lambda value: f"{value:.2f}", return_type=str, when_used="json"),
]


class Item(BaseModel):
    name: str
    price: Money
    qty: int = Field(ge=1)


class Invoice(BaseModel):
    items: list[Item] = Field(min_length=1)
    discount: Money = Decimal("0")

    @model_validator(mode="after")
    def discount_not_above_subtotal(self):
        if self.discount > sum((i.price * i.qty for i in self.items), Decimal("0")):
            raise ValueError("desconto maior que o total")
        return self

    @computed_field
    @property
    def total(self) -> Money:
        return _quantize(sum((i.price * i.qty for i in self.items), Decimal("0")) - self.discount)
