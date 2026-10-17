"""Gabarito do exercício 1."""
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Address(BaseModel):
    model_config = ConfigDict(extra="forbid")
    street: str
    city: str
    zip_code: str

    @field_validator("street", "city")
    @classmethod
    def not_blank(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("não pode ficar em branco")
        return value

    @field_validator("zip_code")
    @classmethod
    def zip_digits(cls, value):
        digits = value.replace("-", "")
        if not re.fullmatch(r"\d{8}", digits):
            raise ValueError("CEP deve ter 8 dígitos")
        return digits


class User(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    email: str
    age: int = Field(ge=0, le=150)
    tags: list[str] = []
    address: Address | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = " ".join(value.split())
        if not value:
            raise ValueError("nome em branco")
        return value

    @field_validator("email")
    @classmethod
    def lower_email(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("e-mail inválido")
        return value

    @field_validator("tags")
    @classmethod
    def unique_tags(cls, value):
        seen, out = set(), []
        for tag in value:
            lowered = tag.lower()
            if lowered not in seen:
                seen.add(lowered)
                out.append(lowered)
        return out
