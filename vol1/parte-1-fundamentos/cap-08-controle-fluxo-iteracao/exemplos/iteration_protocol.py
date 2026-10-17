"""O protocolo de iteracao: o que o for faz por baixo."""
import dis

numbers = [10, 20]
iterator = iter(numbers)          # lista -> iterador
print(type(numbers).__name__, type(iterator).__name__)
print(next(iterator))
print(next(iterator))
try:
    next(iterator)
except StopIteration:
    print("StopIteration: acabou")
print(next(iterator, "padrao"))   # iterador esgotado continua esgotado

# iteravel x iterador
print(iter(iterator) is iterator)     # iterador e iteravel de si mesmo
print(iter(numbers) is numbers)       # lista nao e
print(iter(numbers) is iter(numbers)) # cada iter() cria um novo

# o for escrito "na mao"
def manual_for(iterable):
    iterator = iter(iterable)
    while True:
        try:
            item = next(iterator)
        except StopIteration:
            break
        print("item:", item)


manual_for("ab")

# iteradores sao de uma passada so
squares = (n * n for n in range(3))
print(list(squares), list(squares))

# bytecode
def loop(items):
    total = 0
    for item in items:
        total += item
    return total


dis.dis(loop)

# iteracao antiga: __getitem__ com IndexError tambem funciona
class Old:
    def __getitem__(self, index):
        if index >= 3:
            raise IndexError
        return index * 100


print(list(Old()))
# iter(callable, sentinela): chama ate devolver a sentinela
values = iter([3, 2, 1, 0, 9])
print(list(iter(lambda: next(values), 0)))
