"""Exercício 1: validar e normalizar nomes com acentos."""


def normalize_name(name: str) -> str:
    """Devolva ``name`` normalizado, ou levante ``ValueError``.

    Regras:
    - converta para NFC (``é`` sempre como um único ponto de código);
    - remova espaços nas pontas e colapse qualquer sequência de espaços
      (inclusive ``\\t`` e o espaço sem quebra ``\\u00a0``) em um só ' ';
    - cada caractere deve ser letra (``str.isalpha``), espaço, hífen ou
      apóstrofo (``'``); caso contrário, ``ValueError``;
    - nome vazio após a limpeza também é ``ValueError``.

    Exemplos::

        normalize_name("  Jose\\u0301   da  Silva ") == "José da Silva"
        normalize_name("D'Ávila-Souza") == "D'Ávila-Souza"
        normalize_name("R2D2")  # ValueError

    Dica: a letra acentuada decomposta (``e`` + U+0301) NÃO é ``isalpha``
    no segundo ponto de código, então normalize ANTES de validar.
    """
    raise NotImplementedError
