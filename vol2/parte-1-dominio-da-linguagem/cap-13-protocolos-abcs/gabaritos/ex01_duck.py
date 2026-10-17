"""Gabarito do exercício 1."""


def copy_stream(source, target, chunk_size=4):
    total = 0
    while chunk := source.read(chunk_size):        # vazio ("" ou b"") encerra
        target.write(chunk)
        total += len(chunk)
    return total


def quack_all(items, method="speak"):
    results = []
    for item in items:
        try:
            func = getattr(item, method)            # só o ACESSO é protegido
        except AttributeError:
            continue                                 # ignora quem não tem o método
        results.append(func())                       # erros daqui para dentro sobem
    return results
