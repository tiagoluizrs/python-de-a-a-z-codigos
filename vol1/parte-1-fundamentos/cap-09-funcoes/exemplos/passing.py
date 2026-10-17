"""Passagem por referência de objeto: mutar x reatribuir."""


def mutate(items):
    items.append(99)


def rebind(items):
    items = items + [99]
    return items


def show_ids(items):
    print("inside :", id(items) == outer_id)


data = [1, 2]
outer_id = id(data)
show_ids(data)
mutate(data)
print(data)
rebind(data)
print(data)
print(rebind(data), data)


def inc(n):
    n += 1
    return n

x = 1
inc(x)
print(x)

t = ([1], 2)
def touch(tp):
    tp[0].append(5)
touch(t)
print(t)
