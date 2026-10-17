"""Gabarito do exercício 4."""
from typing import Literal

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SHOP_", env_nested_delimiter="__", env_file=None, extra="ignore")

    environment: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = False
    port: int = Field(8000, ge=1, le=65535)
    allowed_hosts: list[str] = ["localhost"]
    secret_key: SecretStr
    database_url: SecretStr
    redis: Redis = Redis()

    @field_validator("secret_key")
    @classmethod
    def long_enough(cls, value):
        if len(value.get_secret_value()) < 8:
            raise ValueError("a chave secreta precisa de pelo menos 8 caracteres")
        return value

    @field_validator("database_url")
    @classmethod
    def known_database(cls, value):
        if not value.get_secret_value().startswith(("postgresql://", "mysql://")):
            raise ValueError("database_url deve começar com postgresql:// ou mysql://")
        return value

    @model_validator(mode="after")
    def production_rules(self):
        if self.environment == "prod":
            if self.debug:
                raise ValueError("debug não pode ser ligado em prod")
            if "*" in self.allowed_hosts:
                raise ValueError("* não é permitido em prod")
        return self
