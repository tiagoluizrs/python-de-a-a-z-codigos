"""Alvo do exercício 4."""


def notify_overdue(loans, mailer, today):
    """Avisa por e-mail quem tem livros em atraso.

    ``loans``: lista de dicts ``{"borrower": email, "title": str, "due": date, "returned": bool}``.
    Um empréstimo está em atraso se ``due < today`` e não foi devolvido. Cada leitor
    recebe UM e-mail (``mailer.send(to, subject)``) com o assunto
    ``"<n> livro(s) em atraso"``, onde ``n`` é a quantidade de atrasos dele.
    Devolve quantos e-mails foram enviados. Ordem de envio: pela primeira aparição."""
    overdue = {}
    for loan in loans:
        if loan["due"] < today:
            overdue[loan["borrower"]] = overdue.get(loan["borrower"], 0) + 1
    for borrower, count in overdue.items():
        mailer.send(borrower, f"{count} livro(s) em atraso")
    return len(overdue)
