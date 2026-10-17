"""Alterar uma chave depois de inseri-la 'perde' a entrada."""


class Key:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value == other.value


key = Key(1)
table = {key: "x"}
key.value = 2                     # mutação: o hash mudou

print("mesmo objeto:", key in table)
print("Key(2)      :", Key(2) in table)
print("Key(1)      :", Key(1) in table)
print("len         :", len(table))   # a entrada continua lá, inalcançável


class OnlyEq:
    def __eq__(self, other):
        return True


class OnlyHash:
    def __hash__(self):
        return 1


try:
    hash(OnlyEq())
except TypeError as error:
    print("só __eq__  :", error)
print("só __hash__:", hash(OnlyHash()), OnlyHash() == OnlyHash())

nan = float("nan")
table = {nan: 1}
print("nan in {nan}:", nan in table, "| outro nan:", float("nan") in table,
      "| duas chaves nan:", len({nan: 1, float("nan"): 2}))
