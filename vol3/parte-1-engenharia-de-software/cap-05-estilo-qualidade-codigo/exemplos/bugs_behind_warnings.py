"""Os avisos do linter apontam bugs de verdade: cada um com sua consequência."""
import time

# B006: argumento padrão mutável (o Capítulo 9 do Volume 1)
def add(item, bucket=[]):
    bucket.append(item)
    return bucket


add(1)
print("B006:", add(2))                                  # [1, 2]: a lista é compartilhada


# E711: == None chama __eq__, que pode ser sobrescrito
class AlwaysEqual:
    def __eq__(self, other):
        return True


obj = AlwaysEqual()
print("E711: obj == None ->", obj == None, "| obj is None ->", obj is None)   # noqa: E711


# E722: except sem tipo engole KeyboardInterrupt e SystemExit
def swallow():
    try:
        raise KeyboardInterrupt
    except:                                             # noqa: E722
        return "engoliu o Ctrl+C"


print("E722:", swallow())


# E712 / is: == True aceita 1 e 1.0
flag = 1
print("E712: flag == True ->", flag == True, "| flag is True ->", flag is True)   # noqa: E712


# F841/F401 também: o nome sombreado e o import não usado escondem erros de digitação
def total(prices):
    totl = sum(prices)
    return 0                                            # noqa: F841 (o resultado calculado foi perdido)


print("F841: total([1, 2, 3]) ->", total([1, 2, 3]))


# E741 / A001: nomes que sombreiam builtins
list = [3, 1, 2]                                        # noqa: A001
try:
    sorted_copy = list(range(3))
except TypeError as error:
    print("A001: depois de `list = [...]`, list(...) falha:", error)
del list

# SIM/C4/PLC0200: a forma mais curta é também a mais rápida
import timeit


def _manual(items):
    result = []
    for index in range(len(items)):
        result.append(items[index] * 2)
    return result


data = [n for n in range(1000)]
loop = min(timeit.repeat(lambda: [x * 2 for x in data], number=2000, repeat=3)) / 2000
manual = min(timeit.repeat(lambda: _manual(data), number=2000, repeat=3)) / 2000
print(f"C4/PLC0200: compreensão {loop * 1e6:.1f} us | range(len()) + append {manual * 1e6:.1f} us")
