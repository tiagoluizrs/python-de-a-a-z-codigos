"""Gabarito do exercício 3."""
import threading


class Account:
    def __init__(self, number, balance=0):
        self.number = number
        self._balance = balance
        self.lock = threading.Lock()

    @property
    def balance(self):
        with self.lock:
            return self._balance

    def _deposit(self, amount):
        self._balance += amount

    def _withdraw(self, amount):
        if amount <= 0 or amount > self._balance:
            raise ValueError("saldo insuficiente ou valor inválido")
        self._balance -= amount

    def deposit(self, amount):
        with self.lock:
            self._deposit(amount)

    def withdraw(self, amount):
        with self.lock:
            self._withdraw(amount)


def transfer(source, target, amount):
    if source is target:
        raise ValueError("origem e destino iguais")
    first, second = sorted((source, target), key=lambda account: account.number)
    with first.lock, second.lock:
        source._withdraw(amount)
        target._deposit(amount)
