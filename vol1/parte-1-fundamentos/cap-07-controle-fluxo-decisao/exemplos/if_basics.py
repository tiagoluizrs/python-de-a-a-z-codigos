"""Fundamentos de if/elif/else: veracidade, escopo, encadeamento."""


def classify(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 70:
        return "B"
    else:
        return "C"


print([classify(s) for s in (95, 70, 10)])

# Veracidade (Capítulo 3): valores "vazios" são falsos
for value in (0, 0.0, "", [], {}, None, "0", [0], 0.1):
    print(f"{value!r:>6} -> {bool(value)}")

# 'if x' versus 'if x is None'
def describe(count):
    if count is None:
        return "sem dado"
    if not count:
        return "zero"
    return "positivo"


print(describe(None), describe(0), describe(3))

# Encadeamento de comparações
age = 25
print(18 <= age < 65)

# Expressão condicional
label = "adult" if age >= 18 else "minor"
print(label)

# Sem escopo de bloco: variáveis do if vazam
if age > 20:
    status = "ok"
    inner = age * 2
print(status, inner)

# Variável criada em ramo não executado não existe
if age > 100:
    never = 1
try:
    print(never)
except NameError as exc:
    print(type(exc).__name__, exc)

# pass: bloco vazio
if age > 100:
    pass  # ainda não implementado
else:
    print("else executou")

# Operador morsa (Capítulo 4) em condição
items = [1, 2, 3, 4]
if (size := len(items)) > 3:
    print("many items:", size)


# Veracidade de objetos próprios: __bool__ e, se faltar, __len__
class Bag:
    def __init__(self, *things):
        self.things = things

    def __len__(self):
        return len(self.things)


print(bool(Bag()), bool(Bag(1)))

# Armadilha clássica: comparar com True/False
flag = 5
if flag:
    print("flag é verdadeiro")
if flag == True:
    print("não imprime: 5 == True é False")
print(flag == True, flag is True)
