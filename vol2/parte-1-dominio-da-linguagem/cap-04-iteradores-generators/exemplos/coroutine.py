"""Geradores como corrotinas: send, throw, close."""
import inspect


def averager():
    total = 0.0
    count = 0
    average = None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


avg = averager()
try:
    avg.send(10)
except TypeError as exc:
    print("TypeError:", exc)
print(next(avg))          # "primar" o gerador
print(avg.send(10), avg.send(20), avg.send(60))


def resilient():
    try:
        while True:
            try:
                yield
            except ValueError as exc:
                print("  tratou", exc)
    finally:
        print("  limpeza")


r = resilient()
next(r)
r.throw(ValueError("ruim"))
print(inspect.getgeneratorstate(r))
r.close()
print(inspect.getgeneratorstate(r))
r.close()                  # idempotente

try:
    next(r)
except StopIteration:
    print("StopIteration apos close")


def stubborn():
    try:
        yield 1
    except GeneratorExit:
        print("  GeneratorExit recebido")
        yield "nao deveria"


s = stubborn()
next(s)
try:
    s.close()
except RuntimeError as exc:
    print("RuntimeError:", exc)


def gen_throw():
    yield 1
    yield 2


t = gen_throw()
next(t)
try:
    t.throw(KeyError("boom"))
except KeyError as exc:
    print("propagou", exc, inspect.getgeneratorstate(t))


# close no coletor de lixo
def noisy_close():
    try:
        yield 1
    finally:
        print("  finally rodou na coleta")


n = noisy_close()
next(n)
del n
print("depois do del")
