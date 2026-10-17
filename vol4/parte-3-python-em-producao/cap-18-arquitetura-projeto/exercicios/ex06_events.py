"""Exercício 6: um barramento de EVENTOS DE DOMÍNIO em processo (desacopla o caso de uso dos efeitos colaterais)."""


class EventBus:
    """Publica eventos para quem se inscreveu.

    * ``subscribe(event_type, handler)``: ``handler(event)`` é chamado para eventos cujo tipo é ``event_type`` OU uma subclasse dele
      (inscrever-se em ``object`` recebe tudo); o mesmo handler inscrito duas vezes para o mesmo tipo roda UMA vez por evento;
    * ``publish(event)``: chama os handlers na ORDEM de inscrição; a falha de um handler (qualquer ``Exception``) NÃO impede os
      seguintes e NÃO propaga: ela é registrada em ``bus.failures`` como ``(event, handler, exception)``; devolve quantos handlers
      rodaram com sucesso;
    * ``publish_all(events)``: publica em ordem e devolve a soma dos sucessos; se um handler publicar um evento NOVO durante o
      tratamento (``bus.publish`` dentro do handler), esse evento é tratado DEPOIS dos que já estavam na fila (fila FIFO, sem
      recursão), mas ainda dentro da mesma chamada;
    * ``unsubscribe(event_type, handler)``: remove a inscrição (inexistente: ignore);
    * ``failures``: a lista (somente leitura para o chamador: devolva uma cópia) das falhas."""

    def __init__(self):
        raise NotImplementedError

    def subscribe(self, event_type: type, handler) -> None:
        raise NotImplementedError

    def unsubscribe(self, event_type: type, handler) -> None:
        raise NotImplementedError

    def publish(self, event) -> int:
        raise NotImplementedError

    def publish_all(self, events) -> int:
        raise NotImplementedError

    @property
    def failures(self) -> list:
        raise NotImplementedError
