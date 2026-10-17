"""Exercício 4: configuração tipada com pydantic-settings."""
from pydantic_settings import BaseSettings  # noqa: F401


class AppSettings(BaseSettings):
    """Variáveis com o prefixo ``SHOP_`` (``env_prefix``), delimitador aninhado ``__``, sem ler arquivo ``.env``
    (``env_file=None``) e ignorando variáveis desconhecidas:

    * ``environment``: ``"dev"``, ``"staging"`` ou ``"prod"`` (``Literal``); padrão ``"dev"``;
    * ``debug``: bool; padrão ``False``; em ``prod`` NÃO pode ser ``True`` (``ValueError`` num ``model_validator``
      com a mensagem ``"debug não pode ser ligado em prod"``);
    * ``port``: inteiro de 1 a 65535; padrão ``8000``;
    * ``allowed_hosts``: lista de textos (aceita JSON na variável: ``'["a", "b"]'``); padrão ``["localhost"]``;
      em ``prod`` não pode conter ``"*"`` (``"* não é permitido em prod"``);
    * ``secret_key``: ``SecretStr`` OBRIGATÓRIO, com no mínimo 8 caracteres (``min_length`` no valor secreto);
    * ``database_url``: ``SecretStr`` OBRIGATÓRIO que comece com ``postgresql://`` ou ``mysql://``;
    * ``redis`` aninhado: ``host`` (padrão ``"localhost"``) e ``port`` (padrão ``6379``) via ``SHOP_REDIS__HOST`` etc.
      (use um modelo ``BaseModel`` aninhado, com padrão)."""
