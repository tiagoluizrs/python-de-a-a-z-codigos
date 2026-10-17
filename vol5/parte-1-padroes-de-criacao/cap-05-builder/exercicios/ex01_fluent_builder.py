"""Exercício 1: um builder fluente (mutável, como no GoF) para montar uma requisição HTTP."""
import json
from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    headers: tuple          # tuplas ``(nome, valor)``, na ordem em que foram acrescentadas
    params: tuple           # tuplas ``(nome, valor)``
    body: str | None = None

    @property
    def full_url(self) -> str:
        """``url`` e, se houver parâmetros, ``?`` + ``urlencode(params)`` (ou ``&`` se a url já tem ``?``)."""
        raise NotImplementedError


class RequestBuilder:
    """Cada método devolve ``self`` (interface fluente), exceto ``build``.

    * ``method(m)``: guarda o método em MAIÚSCULAS; só ``GET``, ``POST``, ``PUT``, ``DELETE``: outro, ``ValueError(f"método inválido: {m}")``;
      sem chamar ``method``, o padrão é ``GET``;
    * ``url(u)``: obrigatória; ``build()`` sem ela: ``ValueError("url obrigatória")``;
    * ``header(nome, valor)``: acrescenta (nomes repetidos são ACRESCENTADOS, não substituídos);
    * ``param(nome, valor)``: acrescenta um parâmetro de consulta (``str(valor)``);
    * ``json_body(objeto)``: define o corpo como ``json.dumps(objeto)`` e acrescenta o cabeçalho ``("Content-Type", "application/json")``;
    * ``build()``: devolve uma ``Request``. ``GET`` ou ``DELETE`` com corpo: ``ValueError("GET não aceita corpo")`` (com o nome do método).
      O builder pode ser reaproveitado: depois de ``build()``, novos passos NÃO alteram a ``Request`` já criada (copie as listas)."""

    def method(self, m: str):
        raise NotImplementedError

    def url(self, u: str):
        raise NotImplementedError

    def header(self, name: str, value: str):
        raise NotImplementedError

    def param(self, name: str, value):
        raise NotImplementedError

    def json_body(self, obj):
        raise NotImplementedError

    def build(self) -> Request:
        raise NotImplementedError
