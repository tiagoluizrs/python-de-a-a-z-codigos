"""Exercício 2: um filtro que impede segredos de irem parar nos logs."""

SENSITIVE_KEYS = {"password", "senha", "token", "authorization", "api_key", "cpf", "card_number", "secret"}


def redact(value, max_len: int = 200):
    """Devolve uma CÓPIA de ``value`` (dicts, listas e tuplas aninhados; o original não pode mudar) com:

    * em um dict, o valor de qualquer chave (sem diferenciar maiúsculas de minúsculas) em ``SENSITIVE_KEYS``
      trocado por ``"***"`` (inclusive quando for um dict ou uma lista; não desça nele);
    * em qualquer texto: ``Bearer <token>`` (o token é uma sequência de letras, números, ``.``, ``-``, ``_``)
      vira ``Bearer ***``, e um e-mail vira o primeiro caractere do usuário + ``***@`` + o domínio
      (``ana@exemplo.com`` -> ``a***@exemplo.com``);
    * texto maior que ``max_len`` cortado em ``max_len`` caracteres mais ``"…(+N chars)"``, com ``N`` quantos foram
      cortados (a redação dos dois itens acima vem ANTES do corte);
    * listas continuam listas e tuplas continuam tuplas; outros tipos (números, ``None``, ``bool``) passam intactos."""
    raise NotImplementedError


def redact_event(logger, method, event_dict: dict) -> dict:
    """Um *processor* do structlog: aplica ``redact`` ao ``event_dict`` e devolve o resultado (um dict novo)."""
    raise NotImplementedError
