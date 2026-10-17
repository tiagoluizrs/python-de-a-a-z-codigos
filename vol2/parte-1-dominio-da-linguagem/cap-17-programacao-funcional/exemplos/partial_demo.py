"""partial, Placeholder (3.14+), partialmethod e o laço com closures."""
import timeit
from functools import Placeholder, partial, partialmethod

to_int_binary = partial(int, base=2)
print(to_int_binary("101"), to_int_binary.func, to_int_binary.args, to_int_binary.keywords)
print(partial(print, "log:"))                              # repr informativo

# Argumentos posicionais entram na ordem; os nomeados podem ser sobrescritos
greet = partial("{} {}!".format, "Olá")
print(greet("Ana"))
sep_dash = partial(print, sep="-")
sep_dash(1, 2, 3)
sep_dash(1, 2, 3, sep="+")

# Placeholder: reservar posições (3.14+)
square = partial(pow, Placeholder, 2)                      # pow(?, 2)
print(square(5), square(10))
divide_by_two = partial(divmod, Placeholder, 2)
print(divide_by_two(9))

# O objeto é inspecionável (o lambda não é)
print(callable(square), type(square).__name__)

# O laço com closures (Capítulo 2) e o partial
callbacks_late = [lambda: i for i in range(3)]
callbacks_partial = [partial(lambda i: i, i) for i in range(3)]
print([c() for c in callbacks_late], [c() for c in callbacks_partial])


# partialmethod: partial para métodos
class Device:
    def set(self, key, value):
        setattr(self, key, value)

    set_on = partialmethod(set, "state", "on")
    set_off = partialmethod(set, "state", "off")


device = Device()
device.set_on()
print(device.state)
device.set_off()
print(device.state)

# Custo: partial x lambda x função direta
def add(a, b):
    return a + b


add_one_partial = partial(add, 1)
add_one_lambda = lambda b: add(1, b)
ns = dict(add=add, add_one_partial=add_one_partial, add_one_lambda=add_one_lambda)
print("chamada (ns):")
for label, statement in [("add(1, 2)", "add(1, 2)"), ("partial", "add_one_partial(2)"),
                         ("lambda", "add_one_lambda(2)")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=500_000, repeat=5)) / 500_000
    print(f"  {label:<10}{seconds * 1e9:7.1f}")
