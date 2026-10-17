"""Gabarito do exercício 1."""


def make_multipliers(n):
    # Uma fábrica interna cria um escopo novo por chamada: cada
    # lambda captura o ``factor`` do SEU escopo, não o do laço.
    def make(factor):
        return lambda x: x * factor

    return [make(i) for i in range(n)]


def make_accumulator(start=0):
    value = start   # variável da fábrica, capturada pelas três funções

    def add(x):
        nonlocal value          # sem isso, value += x seria local
        value += x
        return value

    def total():
        return value            # só leitura: nonlocal desnecessário

    def reset():
        nonlocal value
        value = start

    return add, total, reset
