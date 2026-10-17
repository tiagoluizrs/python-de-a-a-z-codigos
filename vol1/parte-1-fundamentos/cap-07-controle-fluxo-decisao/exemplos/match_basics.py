"""match/case: literais, captura, OR, curinga, guards."""


def http_text(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 301 | 302:
            return "redirect"
        case 404:
            return "not found"
        case 500 | 502 | 503:
            return "server error"
        case _:
            return "other"


print([http_text(s) for s in (200, 302, 404, 503, 418)])


# Literais: None, True, False comparam com "is"; números com "=="
def kind(value):
    match value:
        case None:
            return "none"
        case True:
            return "true"
        case False:
            return "false"
        case 0:
            return "zero"
        case "":
            return "empty str"
        case str():
            return "str"
        case _:
            return "other"


print([kind(v) for v in (None, True, False, 0, 1, "", "x")])
# 1 == True, mas "case True" usa "is": 1 cai em "other"
print(kind(1), kind(1.0), kind(0.0))

# Captura e as
match (3, 4):
    case (x, y):
        print("captured", x, y)

match 42:
    case int() as number:
        print("as:", number)

# Guard
def sign(n):
    match n:
        case 0:
            return "zero"
        case n if n < 0:
            return "negative"
        case _:
            return "positive"


print(sign(-3), sign(0), sign(8))

# Quando nada casa: nenhum ramo, nenhum erro
match "unknown":
    case "a":
        print("a")
print("nada casou e nada aconteceu")

# match avalia o sujeito UMA vez
def noisy():
    print("noisy() chamada")
    return 2


match noisy():
    case 1:
        print("one")
    case 2:
        print("two")
    case 3:
        print("three")
