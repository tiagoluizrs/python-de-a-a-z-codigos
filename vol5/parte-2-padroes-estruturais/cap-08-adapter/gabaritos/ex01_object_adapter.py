"""Gabarito do exercício 1."""
from typing import Protocol


class Notifier(Protocol):
    def notify(self, user: str, message: str, level: str = "normal") -> bool: ...


class OldMailer:
    def __init__(self):
        self.sent = []

    def send_mail(self, to_address, subject, body, priority):
        if not to_address:
            return 1
        self.sent.append((to_address, subject, body, priority))
        return 0


class SmsGateway:
    def __init__(self):
        self.pushed = []

    def push(self, number, text):
        if len(text) > 160:
            raise ValueError("texto longo demais")
        self.pushed.append((number, text))
        return {"accepted": bool(number), "id": f"sms-{len(self.pushed)}"}


PRIORITY = {"low": 1, "normal": 3, "high": 5}


def _check_level(level):
    if level not in PRIORITY:
        raise ValueError(f"nível inválido: {level}")


class MailerAdapter:
    def __init__(self, mailer, directory):
        self._mailer, self._directory = mailer, directory

    def notify(self, user, message, level="normal"):
        if user not in self._directory:
            raise LookupError(f"usuário sem e-mail: {user}")
        _check_level(level)
        return self._mailer.send_mail(self._directory[user], f"[{level.upper()}] {message[:30]}", message, PRIORITY[level]) == 0


class SmsAdapter:
    def __init__(self, gateway, phones):
        self._gateway, self._phones = gateway, phones

    def notify(self, user, message, level="normal"):
        if user not in self._phones:
            raise LookupError(f"usuário sem telefone: {user}")
        _check_level(level)
        text = f"{level.upper()}: {message}"
        if len(text) > 160:
            text = text[:159] + "…"
        return self._gateway.push(self._phones[user], text)["accepted"]


def notify_all(notifiers, user, message, level="normal"):
    results = []
    for notifier in notifiers:
        try:
            results.append(notifier.notify(user, message, level))
        except LookupError:
            results.append(False)
    return results
