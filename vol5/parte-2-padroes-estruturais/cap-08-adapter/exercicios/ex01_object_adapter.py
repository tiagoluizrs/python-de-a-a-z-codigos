"""Exercício 1: dois adaptadores de OBJETO para a mesma interface (``Notifier``), sobre duas classes legadas que não podemos editar."""
from typing import Protocol


class Notifier(Protocol):
    """A interface que o NOSSO código espera."""

    def notify(self, user: str, message: str, level: str = "normal") -> bool: ...


# ---- as classes legadas (NÃO edite) ----
class OldMailer:
    """Envia e-mail. ``send_mail`` devolve 0 se enviou e 1 se o endereço é vazio."""

    def __init__(self):
        self.sent = []

    def send_mail(self, to_address: str, subject: str, body: str, priority: int) -> int:
        if not to_address:
            return 1
        self.sent.append((to_address, subject, body, priority))
        return 0


class SmsGateway:
    """Envia SMS. ``push`` devolve ``{"accepted": bool, "id": str}``; um texto com mais de 160 caracteres levanta ``ValueError``."""

    def __init__(self):
        self.pushed = []

    def push(self, number: str, text: str) -> dict:
        if len(text) > 160:
            raise ValueError("texto longo demais")
        self.pushed.append((number, text))
        return {"accepted": bool(number), "id": f"sms-{len(self.pushed)}"}


class MailerAdapter:
    """``MailerAdapter(mailer, directory)``; ``directory`` é ``{usuario: e-mail}``. ``notify(user, message, level)``:

    * usuário que não está em ``directory``: ``LookupError(f"usuário sem e-mail: {user}")``;
    * ``level`` -> prioridade: ``"low"`` = 1, ``"normal"`` = 3, ``"high"`` = 5; outro nível: ``ValueError(f"nível inválido: {level}")``;
    * assunto: ``f"[{LEVEL}] {message[:30]}"`` (``LEVEL`` em maiúsculas); corpo: a própria mensagem;
    * devolve ``True`` se ``send_mail`` devolveu 0, ``False`` caso contrário."""

    def __init__(self, mailer, directory: dict):
        raise NotImplementedError

    def notify(self, user: str, message: str, level: str = "normal") -> bool:
        raise NotImplementedError


class SmsAdapter:
    """``SmsAdapter(gateway, phones)``; ``phones`` é ``{usuario: número}``. ``notify(user, message, level)``:

    * usuário que não está em ``phones``: ``LookupError(f"usuário sem telefone: {user}")``;
    * ``level`` precisa ser ``"low"``, ``"normal"`` ou ``"high"`` (mesmo ``ValueError``); o texto enviado é ``f"{LEVEL}: {message}"`` e, se passar de
      160 caracteres, é CORTADO em 159 e termina com ``"…"`` (assim o gateway nunca levanta ``ValueError``);
    * devolve ``gateway.push(...)["accepted"]``."""

    def __init__(self, gateway, phones: dict):
        raise NotImplementedError

    def notify(self, user: str, message: str, level: str = "normal") -> bool:
        raise NotImplementedError


def notify_all(notifiers: list, user: str, message: str, level: str = "normal") -> list[bool]:
    """Chama ``notify`` em cada notificador (na ordem) e devolve a lista de resultados. Um notificador que levanta ``LookupError`` conta como ``False``
    (o usuário não tem aquele canal) e os seguintes continuam; qualquer OUTRA exceção sobe."""
    raise NotImplementedError
