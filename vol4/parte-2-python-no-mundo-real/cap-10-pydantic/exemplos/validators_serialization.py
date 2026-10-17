"""Validadores, campos calculados e serialização."""
import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ValidationError, computed_field, field_serializer, field_validator, model_validator


class Order(BaseModel):
    customer: str
    qty: int
    price: Decimal
    placed: dt.datetime
    coupon: str | None = None

    @field_validator("customer")
    @classmethod
    def normalize_customer(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("cliente em branco")
        return value.title()

    @field_validator("qty")
    @classmethod
    def positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("a quantidade deve ser positiva")
        return value

    @model_validator(mode="after")
    def coupon_needs_minimum(self):
        if self.coupon and self.qty * self.price < 50:
            raise ValueError("o cupom exige um pedido de pelo menos 50")
        return self

    @computed_field
    @property
    def total(self) -> Decimal:
        return self.qty * self.price

    @field_serializer("placed")
    def placed_as_utc_iso(self, value: dt.datetime) -> str:
        return value.astimezone(dt.UTC).isoformat()


order = Order.model_validate({"customer": "  ana   souza ", "qty": "3", "price": "9.90", "placed": "2026-10-13T09:30:00-03:00"})
print("normalizado:", order.customer, "| total calculado:", order.total)
print("model_dump()      :", order.model_dump())
print("model_dump(json)  :", order.model_dump(mode="json"))
print("model_dump_json() :", order.model_dump_json())
print("exclude/include   :", order.model_dump(include={"customer", "total"}), order.model_dump(exclude={"placed", "coupon"}, exclude_none=True))

for payload in ({"customer": "x", "qty": 0, "price": "1", "placed": "2026-01-01T00:00:00Z"},
                {"customer": "x", "qty": 1, "price": "10", "placed": "2026-01-01T00:00:00Z", "coupon": "PROMO"}):
    try:
        Order.model_validate(payload)
    except ValidationError as error:
        item = error.errors()[0]
        print("recusado:", item["type"], "|", item["msg"], "| loc:", item["loc"])

# ida e volta: o JSON que sai entra de novo
again = Order.model_validate_json(order.model_dump_json())
print("\nida e volta preserva o objeto:", again.customer == order.customer and again.total == order.total, "| Decimal vira string no JSON (sem perder centavos):", order.model_dump(mode="json")["price"])
print("modos de validador: 'after' recebe o valor já convertido (o comum); 'before' recebe o dado BRUTO (para limpar antes); 'wrap' envolve a validação; model_validator(mode='before') vê o dicionário inteiro")
