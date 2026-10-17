"""pydantic-settings: configuração tipada a partir do ambiente (promessa do Capítulo 12 do Volume 3)."""
import os

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Database(BaseSettings):
    url: SecretStr
    pool_size: int = Field(5, ge=1, le=100)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__", env_file=None, extra="ignore")

    debug: bool = False
    port: int = Field(8000, ge=1, le=65535)
    allowed_hosts: list[str] = ["localhost"]
    api_key: SecretStr
    db: Database

    @field_validator("allowed_hosts")
    @classmethod
    def no_wildcard_in_prod(cls, hosts):
        if "*" in hosts:
            raise ValueError("'*' não é permitido")
        return hosts


# 1. tudo vem de variáveis de ambiente (aqui simuladas); os tipos são convertidos e VALIDADOS
os.environ.update({"APP_DEBUG": "yes", "APP_PORT": "9000", "APP_ALLOWED_HOSTS": '["a.example", "b.example"]',
                   "APP_API_KEY": "sk-segredo-123", "APP_DB__URL": "postgresql://u:senha@h/db", "APP_DB__POOL_SIZE": "20"})
settings = Settings()
print("tipos convertidos:", settings.debug, settings.port, settings.allowed_hosts, settings.db.pool_size)
print("segredos mascarados em print/repr/log:", settings.api_key, "|", repr(settings.db.url))
print("o valor real, só quando você pede:", settings.api_key.get_secret_value()[:6] + "...")
print("model_dump() também mascara:", settings.model_dump()["api_key"])

# 2. falha CEDO, na partida, com todas as mensagens
os.environ.update({"APP_PORT": "70000", "APP_ALLOWED_HOSTS": '["*"]'})
del os.environ["APP_API_KEY"]
try:
    Settings()
except ValidationError as error:
    print("\nconfiguração inválida (a aplicação nem sobe):")
    for item in error.errors():
        print("  ", ".".join(map(str, item["loc"])), "->", item["msg"][:60])

# 3. ordem de prioridade: argumentos > ambiente > .env > padrões
os.environ["APP_PORT"] = "9000"
print("\nsobrescrever em código (testes):", Settings(port=1234, api_key="x", allowed_hosts=["t"]).port)
print("prioridade: argumentos do construtor > variáveis de ambiente > arquivo .env > valores padrão da classe")
print("segredos em arquivo: secrets_dir='/run/secrets' lê um arquivo por segredo (Docker/Kubernetes secrets, Capítulo 17)")
