"""Exercício 5: pipeline de logs com geradores (memória constante).

Cada linha tem o formato ``"<nivel> <servico> <ms>"``, por exemplo
``"ERROR db 250"``. Linhas em branco ou malformadas devem ser
ignoradas pelo parser. Implemente CADA etapa como gerador:

* ``parse(lines)``: entrega tuplas ``(level, service, ms)`` com ``ms``
  inteiro; ignora linhas inválidas.
* ``only_levels(records, levels)``: filtra pelos níveis (conjunto).
* ``total_by_service(records)``: NÃO é gerador; consome o fluxo e
  devolve ``dict`` ``{servico: (quantidade, soma_ms)}``.

Os testes alimentam o pipeline com 300 mil linhas e exigem pico de
memória pequeno (``tracemalloc``): nenhuma etapa pode criar lista.

Exemplo:
``total_by_service(only_levels(parse(["ERROR db 10", "INFO web 5"]),
{"ERROR"})) == {"db": (1, 10)}``
"""


def parse(lines):
    raise NotImplementedError


def only_levels(records, levels):
    raise NotImplementedError


def total_by_service(records):
    raise NotImplementedError
