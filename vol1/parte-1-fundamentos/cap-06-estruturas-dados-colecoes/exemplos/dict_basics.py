"""Dicionários: criação, acesso, métodos e operadores."""
# Quatro formas de criar o mesmo dicionário
a = {"name": "Ana", "age": 30}
b = dict(name="Ana", age=30)
c = dict([("name", "Ana"), ("age", 30)])
d = dict(zip(["name", "age"], ["Ana", 30]))
print(a == b == c == d)

# fromkeys: todas as chaves com o MESMO valor inicial
print(dict.fromkeys("abc", 0))
shared = dict.fromkeys("ab", [])        # armadilha: a mesma lista
shared["a"].append(1)
print(shared, shared["a"] is shared["b"])

# Acesso
user = {"name": "Ana", "age": 30}
print(user["name"], user.get("email"), user.get("email", "n/a"))
try:
    user["email"]
except KeyError as error:
    print("KeyError:", error)

# setdefault: devolve o valor, criando-o se a chave não existir
groups = {}
groups.setdefault("x", []).append(1)
groups.setdefault("x", []).append(2)
print(groups)

# Remoção
print(user.pop("age"), user.pop("age", None), user)
stack = {"a": 1, "b": 2, "c": 3}
print(stack.popitem(), stack)           # LIFO: o último inserido

# update e operadores | e |= (3.9)
base = {"host": "localhost", "port": 80}
override = {"port": 8080, "debug": True}
print(base | override)                  # novo dict; a direita vence
base |= override                        # no lugar
print(base)
base.update(port=9000)
base.update([("host", "example.org")])
print(base)

# in testa CHAVES
print("port" in base, 9000 in base, 9000 in base.values())
