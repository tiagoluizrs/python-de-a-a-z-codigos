"""Gabarito do exercício 3."""


class Handler:
    def __init__(self):
        self.trace = []

    def handle(self, value):
        self.trace.append("Handler")
        return value


class Strip:
    def handle(self, value):
        self.trace.append("Strip")
        return super().handle(value.strip())          # transforma ANTES, passa adiante


class Upper:
    def handle(self, value):
        self.trace.append("Upper")
        return super().handle(value.upper())


class Exclaim:
    def handle(self, value):
        self.trace.append("Exclaim")
        return super().handle(value) + "!"            # passa adiante e transforma DEPOIS


class Pipeline(Strip, Upper, Exclaim, Handler):
    pass
