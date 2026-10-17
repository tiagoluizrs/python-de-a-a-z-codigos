"""operator: as operações da linguagem como funções."""
import operator
import timeit
from functools import reduce
from operator import attrgetter, itemgetter, methodcaller

# itemgetter: um ou vários itens
print(itemgetter(1)([5, 6]), itemgetter(1, 0)([5, 6]), itemgetter("a")({"a": 1}))

rows = [("ana", 30, "SP"), ("bia", 25, "RJ"), ("caio", 30, "RJ")]
print(sorted(rows, key=itemgetter(1, 0)))                       # idade, depois nome


# attrgetter: atributos, inclusive aninhados com ponto
class User:
    def __init__(self, name, age, city):
        self.name, self.age = name, age
        self.address = type("Address", (), {"city": city})()

    def __repr__(self):
        return f"User({self.name!r})"


users = [User("ana", 30, "SP"), User("bia", 25, "RJ")]
print(sorted(users, key=attrgetter("age")), [attrgetter("address.city")(u) for u in users])

# methodcaller: chama um método pelo nome
print(list(map(methodcaller("upper"), ["a", "b"])), methodcaller("split", ",")("x,y"))

# As funções de operador
print(operator.add(2, 3), operator.mul(2, 3), operator.neg(5), operator.contains([1, 2], 2),
      operator.getitem([1, 2, 3], 1), operator.truth(""), operator.not_(0))
print(reduce(operator.mul, range(1, 6)), operator.is_(None, None), operator.index(True))
print(operator.concat([1], [2]), operator.countOf([1, 1, 2], 1), operator.indexOf("abc", "c"))

# Operadores in-place existem para todos
x = [1]
operator.iadd(x, [2])
print(x)

# Ordenação estável permite ordenar por vários critérios em passadas
people = [("ana", 30), ("bia", 25), ("caio", 30), ("dani", 25)]
step1 = sorted(people, key=itemgetter(0))                      # 2o critério primeiro
step2 = sorted(step1, key=itemgetter(1), reverse=True)         # critério principal depois
print(step2)

# Custo
data = [(i, -i) for i in range(1000)]
objs = [User(str(i), i, "x") for i in range(1000)]
ns = dict(data=data, objs=objs, itemgetter=itemgetter, attrgetter=attrgetter)
print("ordenar 1000 itens (us):")
for label, statement in [("lambda t: t[1]", "sorted(data, key=lambda t: t[1])"),
                         ("itemgetter(1)", "sorted(data, key=itemgetter(1))"),
                         ("lambda u: u.age", "sorted(objs, key=lambda u: u.age)"),
                         ("attrgetter", "sorted(objs, key=attrgetter('age'))")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=1000, repeat=5)) / 1000
    print(f"  {label:<18}{seconds * 1e6:7.1f}")
