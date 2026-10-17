"""Exercício 1: o Bridge clássico: mensagens (abstração) x canais (implementação), combináveis à vontade."""
import copy
from abc import ABC, abstractmethod
from typing import Protocol


class Channel(Protocol):
    def deliver(self, to: str, text: str) -> str: ...


class EmailChannel:
    """``deliver(to, text)``: ``to`` precisa conter ``"@"`` (senão ``ValueError(f"endereço inválido: {to}")``); devolve ``f"EMAIL <{to}>: {text}"``."""

    def deliver(self, to: str, text: str) -> str:
        raise NotImplementedError


class SmsChannel:
    """``deliver(to, text)``: ``to`` precisa começar com ``"+"`` (senão ``ValueError(f"número inválido: {to}")``); o texto é CORTADO em 160 caracteres (os
    primeiros 159 mais ``"…"``, se passar de 160); devolve ``f"SMS {to}: {texto}"``."""

    def deliver(self, to: str, text: str) -> str:
        raise NotImplementedError


class ConsoleChannel:
    """Guarda cada entrega na lista pública ``lines`` (``f"{to}: {text}"``) e devolve ``f"CONSOLE {to}: {text}"``."""

    def __init__(self):
        self.lines = []

    def deliver(self, to: str, text: str) -> str:
        raise NotImplementedError


class Message(ABC):
    """A ABSTRAÇÃO. ``Message(channel)``:

    * ``format(body) -> str`` é abstrato (cada tipo de mensagem formata de um jeito);
    * ``send(to, body)`` devolve ``channel.deliver(to, self.format(body))``: a PONTE;
    * ``channel`` (propriedade) devolve o canal atual; ``with_channel(channel)`` devolve uma CÓPIA RASA (``copy.copy``) da mensagem ligada a outro canal,
      conservando o resto dos atributos (a mensagem original não muda)."""

    def __init__(self, channel: Channel):
        raise NotImplementedError

    @property
    def channel(self) -> Channel:
        raise NotImplementedError

    @abstractmethod
    def format(self, body: str) -> str: ...

    def send(self, to: str, body: str) -> str:
        raise NotImplementedError

    def with_channel(self, channel: Channel) -> "Message":
        raise NotImplementedError


class AlertMessage(Message):
    """``format``: ``f"[ALERTA] {body.upper()}"``."""

    def format(self, body: str) -> str:
        raise NotImplementedError


class ReportMessage(Message):
    """``ReportMessage(channel, title)``; ``format``: ``f"{title}\\n{body}\\n-- fim"`` (com quebras de linha de verdade)."""

    def __init__(self, channel: Channel, title: str):
        raise NotImplementedError

    def format(self, body: str) -> str:
        raise NotImplementedError


class ReminderMessage(Message):
    """``format``: o ``body`` com a primeira letra maiúscula (o resto como está) e `` " (lembrete)"`` no fim; ``body`` vazio: ``ValueError("corpo vazio")``."""

    def format(self, body: str) -> str:
        raise NotImplementedError
