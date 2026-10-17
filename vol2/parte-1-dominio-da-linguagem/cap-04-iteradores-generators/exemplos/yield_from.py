"""yield from: delegacao e valor de retorno."""
import inspect


def inner():
    received = yield 1
    print("  inner recebeu", received)
    yield 2
    return "inner-done"


def outer():
    result = yield from inner()
    print("  outer obteve", result)
    yield 3
    return "outer-done"


g = outer()
print(next(g))
print(g.send("ola"))
print(next(g))
try:
    next(g)
except StopIteration as exc:
    print("StopIteration.value =", exc.value)


# sem yield from, o send nao chega ao interno
def manual():
    for x in inner():
        yield x


m = manual()
next(m)
print(m.send("ola"))   # inner recebeu None


# flatten recursivo
def flatten(items):
    for item in items:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


print(list(flatten([1, [2, [3, (4, 5)]], 6])))
print(list(flatten(["ab", [["cd"]]])))


# yield from em qualquer iteravel
def chain_two(a, b):
    yield from a
    yield from b


print(list(chain_two("ab", range(2))))

# return com valor num gerador
def with_return():
    yield 1
    return 99


print(list(with_return()))
g = with_return()
for _ in g:
    pass
print(inspect.getgeneratorstate(g))
