"""Escopo LEGB, global, nonlocal e UnboundLocalError."""
import dis

x = "global"


def outer():
    x = "enclosing"

    def inner():
        x = "local"
        return x

    return inner(), x


print(outer(), x)
print(len)  # built-in, achado no último elo


def bad():
    print(total)
    total = 0


try:
    bad()
except UnboundLocalError as exc:
    print("UnboundLocalError:", exc)

print(bad.__code__.co_varnames, bad.__code__.co_names)

counter = 0


def bad_inc():
    counter += 1


try:
    bad_inc()
except UnboundLocalError as exc:
    print("UnboundLocalError:", exc)


def good_inc():
    global counter
    counter += 1


good_inc()
print(counter)


def make():
    count = 0

    def step():
        nonlocal count
        count += 1
        return count

    return step


s = make()
s(); print(s())

dis.dis(bad)
print("---")


def reads():
    return x

dis.dis(reads)
