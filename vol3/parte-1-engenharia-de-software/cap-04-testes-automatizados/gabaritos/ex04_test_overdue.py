"""Gabarito do exercício 4."""
from datetime import date
from unittest import mock

from overdue_impl import notify_overdue

TODAY = date(2026, 10, 13)


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject):
        self.sent.append((to, subject))


def loan(borrower, due, returned=False, title="livro"):
    return {"borrower": borrower, "title": title, "due": due, "returned": returned}


def test_no_loans():
    mailer = FakeMailer()
    assert notify_overdue([], mailer, TODAY) == 0 and mailer.sent == []


def test_overdue_loan_notifies():
    mailer = FakeMailer()
    assert notify_overdue([loan("a@x.com", date(2026, 10, 1))], mailer, TODAY) == 1
    assert mailer.sent == [("a@x.com", "1 livro(s) em atraso")]


def test_due_today_is_not_overdue():
    mailer = FakeMailer()
    assert notify_overdue([loan("a@x.com", TODAY)], mailer, TODAY) == 0 and mailer.sent == []


def test_returned_loans_are_ignored():
    mailer = FakeMailer()
    assert notify_overdue([loan("a@x.com", date(2026, 1, 1), returned=True)], mailer, TODAY) == 0
    assert mailer.sent == []


def test_future_loans_are_ignored():
    mailer = FakeMailer()
    assert notify_overdue([loan("a@x.com", date(2026, 11, 1))], mailer, TODAY) == 0


def test_one_email_per_borrower_with_count():
    mailer = FakeMailer()
    loans = [loan("a@x.com", date(2026, 9, 1)), loan("a@x.com", date(2026, 9, 2)), loan("a@x.com", date(2026, 9, 3)),
             loan("b@x.com", date(2026, 9, 1))]
    assert notify_overdue(loans, mailer, TODAY) == 2
    assert mailer.sent == [("a@x.com", "3 livro(s) em atraso"), ("b@x.com", "1 livro(s) em atraso")]


def test_three_borrowers_all_notified():
    mailer = FakeMailer()
    loans = [loan(f"{n}@x.com", date(2026, 9, 1)) for n in "abc"]
    assert notify_overdue(loans, mailer, TODAY) == 3 and len(mailer.sent) == 3


def test_mixed_returned_and_overdue_counts_only_overdue():
    mailer = FakeMailer()
    loans = [loan("a@x.com", date(2026, 9, 1)), loan("a@x.com", date(2026, 9, 1), returned=True), loan("b@x.com", TODAY)]
    assert notify_overdue(loans, mailer, TODAY) == 1
    assert mailer.sent == [("a@x.com", "1 livro(s) em atraso")]


def test_with_mock_mailer():
    mailer = mock.Mock()
    notify_overdue([loan("a@x.com", date(2026, 9, 1))], mailer, TODAY)
    mailer.send.assert_called_once_with("a@x.com", "1 livro(s) em atraso")
