"""Protocolos de conversão: __index__, __int__, __float__, __fspath__, __bytes__."""
import operator
import os


class Port:
    def __init__(self, number):
        self.number = number

    def __index__(self):                # "sou um inteiro de verdade"
        return self.number

    def __int__(self):
        return self.number

    def __float__(self):
        return float(self.number)


port = Port(2)
items = ["a", "b", "c", "d"]
print(items[port], items[Port(0):port], "x" * port, hex(Port(255)))
print(operator.index(port), int(port), float(port))


class OnlyInt:
    def __int__(self):
        return 2


try:
    ["a", "b", "c"][OnlyInt()]
except TypeError as error:
    print("TypeError:", error)
print(int(OnlyInt()), "(int() aceita __int__, mas índices exigem __index__)")


class Report:
    def __init__(self, name):
        self.name = name

    def __fspath__(self):                # "sou um caminho"
        return f"/tmp/{self.name}.txt"

    def __bytes__(self):
        return self.name.encode()


print(os.fspath(Report("q3")), bytes(Report("q3")))
import pathlib
print(pathlib.PurePosixPath(Report("q3")))
