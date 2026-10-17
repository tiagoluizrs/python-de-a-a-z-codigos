"""Exercício 6: corrotina simples com ``send``.

``make_averager()`` devolve um gerador JÁ preparado (primed: já avançou
até o primeiro ``yield``) que recebe números via ``send`` e responde
com a média corrente de tudo que recebeu até ali.

    avg = make_averager()
    avg.send(10)   # 10.0
    avg.send(20)   # 15.0

Se receber ``None`` via ``send``, deve devolver a média atual (ou ``None`` se não houver dados) sem
alterá-la. Ao ser fechado com ``close()``, o gerador registra a
contagem final na lista passada em ``log`` (parâmetro opcional,
``log.append(contagem)``), usando ``try/finally``.

Dica: o gerador precisa de um ``yield`` inicial para ser "primado".
"""


def make_averager(log=None):
    raise NotImplementedError
