"""Exercício 4: escreva testes para ``notify_overdue`` usando um DUBLÊ (fake ou mock).

``notify_overdue(loans, mailer, today)`` (veja ``alvos/overdue/correto.py``): em
atraso é ``due < today`` e não devolvido; UM e-mail por leitor, com assunto
``"<n> livro(s) em atraso"``; devolve quantos e-mails enviou.

Escreva um ``FakeMailer`` (guarda o que recebeu) ou use ``unittest.mock``.
Seus testes precisam passar no correto e matar os 7 mutantes.
"""
from datetime import date

from overdue_impl import notify_overdue

TODAY = date(2026, 10, 13)


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject):
        self.sent.append((to, subject))


def test_sem_emprestimos():
    mailer = FakeMailer()
    assert notify_overdue([], mailer, TODAY) == 0
    assert mailer.sent == []

# escreva os demais testes abaixo
