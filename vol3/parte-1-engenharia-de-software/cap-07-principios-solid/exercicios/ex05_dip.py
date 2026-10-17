"""Exercício 5 (D): um serviço de lembretes SEM relógio, rede ou banco dentro dele: tudo chega por parâmetro."""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Reminder:
    id: int
    due: datetime
    to: str
    text: str


class ReminderService:
    """``ReminderService(store, send, now, max_attempts=3)``:

    * ``store``: um objeto com ``pending() -> list[Reminder]`` (os ainda não enviados) e ``mark_sent(id)``;
    * ``send``: um callable ``send(to, text) -> None`` que pode levantar ``ConnectionError``;
    * ``now``: um callable sem argumentos que devolve o ``datetime`` atual (NUNCA chame ``datetime.now()`` dentro da classe);
    * ``max_attempts``: tentativas de ``send`` por lembrete em UMA chamada de ``run`` (a primeira conta).

    ``run() -> dict`` percorre ``store.pending()`` na ordem recebida e, para cada lembrete com ``due <= now()``: tenta ``send`` até
    ``max_attempts`` vezes (só repete se ``send`` levantar ``ConnectionError``; qualquer OUTRA exceção sobe na hora, sem marcar nada). Se ``send``
    funcionar, chama ``store.mark_sent(id)``. Se esgotar as tentativas, o lembrete fica pendente (``mark_sent`` NÃO é chamado) e continua
    nos próximos. Os que ainda não venceram são ignorados. Devolve ``{"sent": [ids], "failed": [ids], "waiting": [ids]}`` (``waiting`` = os que
    ainda não venceram), cada lista na ordem de ``pending()``. Calcule ``now()`` UMA vez por ``run`` (todos os lembretes são comparados com o
    MESMO instante)."""

    def __init__(self, store, send: Callable[[str, str], None], now: Callable[[], datetime], max_attempts: int = 3):
        raise NotImplementedError

    def run(self) -> dict:
        raise NotImplementedError


def build_service(env: dict, store, smtp_send: Callable[[str, str, str], None] | None = None, clock: Callable[[], datetime] | None = None) -> ReminderService:
    """A RAIZ DE COMPOSIÇÃO: monta o serviço conforme ``env`` (um dict).

    * se ``env`` tem ``"SMTP_HOST"``, ``send`` é ``lambda to, text: smtp_send(env["SMTP_HOST"], to, text)`` (``smtp_send`` precisa ter sido
      dado; senão ``ValueError("smtp_send ausente")``); sem ``SMTP_HOST``, ``send`` acumula as mensagens em uma lista
      acessível como ``service.outbox`` (atribua ``service.outbox = []`` e faça ``send`` chamar ``service.outbox.append((to, text))``);
    * ``clock`` (se dado) é o ``now``; se for ``None``, use ``datetime.now``;
    * ``max_attempts`` vem de ``env.get("MAX_ATTEMPTS", "3")`` convertido para ``int``.
    Devolve o ``ReminderService``."""
    raise NotImplementedError
