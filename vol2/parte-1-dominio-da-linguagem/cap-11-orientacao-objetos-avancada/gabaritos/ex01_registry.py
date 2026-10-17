"""Gabarito do exercício 1."""


class Tracker:
    created = 0                           # atributo de CLASSE: contador compartilhado

    def __init__(self, name):
        self.name = name
        self.events = []                  # criado POR INSTÂNCIA (no __init__)
        Tracker.created += 1              # Tracker., e não self.: não cria atributo de instância

    def record(self, event):
        self.events.append(event)

    @classmethod
    def created_count(cls):
        return cls.created

    @classmethod
    def reset_count(cls):
        cls.created = 0

    @staticmethod
    def is_valid_name(text):
        return isinstance(text, str) and text == text.strip() and text != ""
