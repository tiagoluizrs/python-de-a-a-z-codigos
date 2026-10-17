"""Gabarito do exercício 1."""
import copy
from abc import ABC, abstractmethod
from typing import Protocol


class Channel(Protocol):
    def deliver(self, to: str, text: str) -> str: ...


class EmailChannel:
    def deliver(self, to, text):
        if "@" not in to:
            raise ValueError(f"endereço inválido: {to}")
        return f"EMAIL <{to}>: {text}"


class SmsChannel:
    def deliver(self, to, text):
        if not to.startswith("+"):
            raise ValueError(f"número inválido: {to}")
        if len(text) > 160:
            text = text[:159] + "…"
        return f"SMS {to}: {text}"


class ConsoleChannel:
    def __init__(self):
        self.lines = []

    def deliver(self, to, text):
        self.lines.append(f"{to}: {text}")
        return f"CONSOLE {to}: {text}"


class Message(ABC):
    def __init__(self, channel):
        self._channel = channel

    @property
    def channel(self):
        return self._channel

    @abstractmethod
    def format(self, body): ...

    def send(self, to, body):
        return self._channel.deliver(to, self.format(body))

    def with_channel(self, channel):
        clone = copy.copy(self)
        clone._channel = channel
        return clone


class AlertMessage(Message):
    def format(self, body):
        return f"[ALERTA] {body.upper()}"


class ReportMessage(Message):
    def __init__(self, channel, title):
        super().__init__(channel)
        self.title = title

    def format(self, body):
        return f"{self.title}\n{body}\n-- fim"


class ReminderMessage(Message):
    def format(self, body):
        if not body:
            raise ValueError("corpo vazio")
        return body[0].upper() + body[1:] + " (lembrete)"
