"""Exercício 4: um barramento de eventos (publicar/assinar) com tópicos, curingas e erros isolados."""


class EventBus:
    """Observadores agrupados por TÓPICO (texto como ``"order.created"``).

    * ``subscribe(pattern, fn)``: assina ``fn`` para os tópicos que casam com ``pattern`` (use ``fnmatch.fnmatchcase``: ``"order.*"`` casa ``"order.created"`` e
      ``"order.paid"``; ``"*"`` casa tudo); devolve ``fn``; ``fn`` não chamável: ``TypeError``; o MESMO par ``(pattern, fn)`` duas vezes:
      ``ValueError("já assinado")``;
    * ``unsubscribe(pattern, fn)``: remove; inexistente: ``ValueError("não assinado")``;
    * ``publish(topic, payload=None)``: chama ``fn(topic, payload)`` de CADA assinatura que casa, na ordem em que foram feitas, e devolve quantos observadores foram
      chamados SEM erro; tópico vazio: ``ValueError("tópico vazio")``;
    * erros: uma exceção (``Exception``) em um observador NÃO levanta nada para quem publica nem impede os outros; ela é registrada em ``errors`` como
      ``(topic, nome_da_função, exceção)`` (``nome_da_função`` é ``fn.__name__`` ou, se não tiver, ``repr(fn)``);
    * ``subscribers(topic)``: a lista de funções que receberiam esse tópico, na ordem; ``history``: lista de todos os ``(topic, payload)`` publicados, na ordem
      (inclusive os sem assinante)."""

    def __init__(self):
        raise NotImplementedError

    def subscribe(self, pattern: str, fn):
        raise NotImplementedError

    def unsubscribe(self, pattern: str, fn) -> None:
        raise NotImplementedError

    def publish(self, topic: str, payload=None) -> int:
        raise NotImplementedError

    def subscribers(self, topic: str) -> list:
        raise NotImplementedError

    @property
    def errors(self) -> list:
        raise NotImplementedError

    @property
    def history(self) -> list:
        raise NotImplementedError
