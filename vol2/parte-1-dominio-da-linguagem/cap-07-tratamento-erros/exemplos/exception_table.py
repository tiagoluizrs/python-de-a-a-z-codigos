"""try/except custa zero quando nada falha: a tabela de exceções."""
import dis


def with_try():
    try:
        x = 1
    except ValueError:
        pass
    return x


dis.dis(with_try)
print("tamanho do bytecode:", len(with_try.__code__.co_code), "bytes")
print("co_exceptiontable:", with_try.__code__.co_exceptiontable.hex(" "))
