"""Exercício 1: um modelo de usuário que normaliza e valida."""
from pydantic import BaseModel  # noqa: F401


class Address(BaseModel):
    """``street`` (texto não vazio, sem espaços nas pontas), ``city`` (idem), ``zip_code`` (exatamente 8 dígitos; aceite
    ``"12345-678"`` e devolva ``"12345678"``). Campos extras são PROIBIDOS."""


class User(BaseModel):
    """Campos:

    * ``name``: texto; remove espaços das pontas e colapsa espaços internos repetidos; não pode ficar vazio;
    * ``email``: texto com um ``@`` e um ponto depois dele; guarde em MINÚSCULAS (não use ``EmailStr``);
    * ``age``: inteiro entre 0 e 150 (aceite ``"30"``);
    * ``tags``: lista de textos; remova duplicatas ignorando maiúsculas, mantendo a ordem da 1ª ocorrência e
      guardando em minúsculas; padrão ``[]``;
    * ``address``: ``Address`` opcional (``None`` por padrão);
    * campos extras PROIBIDOS; a instância é IMUTÁVEL (``frozen``);
    * implemente com ``field_validator`` e ``ConfigDict``."""
