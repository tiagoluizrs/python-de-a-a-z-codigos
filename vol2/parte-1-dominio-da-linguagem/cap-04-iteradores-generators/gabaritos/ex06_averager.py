"""Gabarito 6: média corrente com send."""


def _averager(log):
    total = 0
    count = 0
    average = None
    try:
        while True:
            value = yield average
            if value is None:
                continue            # send(None): só consulta
            total += value
            count += 1
            average = total / count
    finally:
        # close() lança GeneratorExit no yield; o finally roda e o
        # gerador termina (não pode haver novo yield aqui dentro)
        if log is not None:
            log.append(count)


def make_averager(log=None):
    gen = _averager(log)
    next(gen)       # "primar": avança até o primeiro yield
    return gen
